"""Core data model for the racing simulation.

The rest of the project reads and updates these classes while playing turns.
"""

from typing import List, Tuple
import logging
import random

_LOGGER = logging.getLogger("racecars.game_state")

_ADJECTIVES = [
    "Red", "Blue", "Green", "Yellow", "Silver", "Black",
    "Swift", "Brave", "Wild", "Mighty", "Fierce", "Lucky"
]

_NOUNS = [
    "Comet", "Falcon", "Tiger", "Eagle", "Rocket", "Panther",
    "Wolf", "Viper", "Storm", "Blaze", "Arrow", "Bolt"
]
class Vector2i:
    def __init__(self, x: int = 0, y: int = 0):
        self.x = int(x)
        self.y = int(y)

    def __add__(self, other):
        if not isinstance(other, Vector2i):
            return NotImplemented
        if isinstance(self, Vertex) or isinstance(other, Vertex):
            return Vertex(self.x + other.x, self.y + other.y)
        return Vector2i(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if not isinstance(other, Vector2i):
            return NotImplemented
        return Vector2i(self.x - other.x, self.y - other.y)

    def __rsub__(self, other):
        if not isinstance(other, Vector2i):
            return NotImplemented
        return Vector2i(other.x - self.x, other.y - self.y)

    def __eq__(self, other):
        if not isinstance(other, Vector2i):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Vector2i(x={self.x}, y={self.y})"

class Vertex(Vector2i):
    def __repr__(self):
        return f"Vertex(x={self.x}, y={self.y})"

class Segment:
    def __init__(self, start: Vertex, end: Vertex):
        self.start = start
        self.end = end

    def __repr__(self):
        return f"Segment(start={self.start}, end={self.end})"

class Car:
    def __init__(self, car_id: int, name: str, pos: Vertex, vel: Vector2i):
        # One Car object stores everything needed to replay and score a single driver.
        self.id = car_id
        self.name = name
        self.pos = pos
        self.vel = vel  # Velocity vector
        self.penalty = 0  # Number of penalty turns remaining
        self.path: List[Segment] = []  # Path history for replay/logging
        self.trail: List[Tuple[int, int]] = []  # Initialize trail as an empty list
        self.driver = None
        self.logger = None
        self._missing_driver_warning_emitted = False

    def __repr__(self):
        return f"Car(id={self.id}, name={self.name}, pos={self.pos}, vel={self.vel}, penalty={self.penalty})"

    def SetDriver(self, driver):
        self.driver = driver
        self._missing_driver_warning_emitted = False

    def PickMove(self, world, targets, validity):
        if self.driver is None:
            if not self._missing_driver_warning_emitted:
                logger = self.logger
                if logger is None:
                    logger = _LOGGER
                logger.warning("Car '%s' has no driver assigned. Returning None move.", self.name)
                self._missing_driver_warning_emitted = True
            return None
        self._missing_driver_warning_emitted = False
        # Forward car instance, world, ordered targets and validity flags to driver
        return self.driver.PickMove(self, world, targets, validity)

class Track:
    def __init__(self, width: int, height: int, road_mask: List[List[bool]], start_vertices: List[Vertex], finish_line: Segment):
        # The track is a grid plus start/finish metadata used by movement validation.
        self.width = width
        self.height = height
        self.road_mask = road_mask  # Binary mask indicating road cells
        self.start_vertices = start_vertices  # List of vertices on the start line
        self.finish_line = finish_line  # Segment representing the finish line

        # Define start_line as a Segment using the first and last start_vertices
        if start_vertices:
            self.start_line = Segment(start_vertices[0], start_vertices[-1])
        else:
            self.start_line = None

    def segment_is_valid(self, p0: Vertex, p1: Vertex) -> bool:
        # We validate a move by sampling every interval between grid-line crossings.
        # If any sampled interval is off-road, the whole move is invalid.
        dx = p1.x - p0.x
        dy = p1.y - p0.y
        if dx == 0 and dy == 0:
            return self._point_has_road(p0.x, p0.y)

        t_values = self._collect_t_values(p0, p1)

        if dx != 0:
            if dx > 0:
                for x in range(p0.x + 1, p1.x):
                    t = (x - p0.x) / dx
                    if t > 0 and t < 1:
                        t_values.append(t)
            else:
                for x in range(p0.x - 1, p1.x, -1):
                    t = (x - p0.x) / dx
                    if t > 0 and t < 1:
                        t_values.append(t)

        if dy != 0:
            if dy > 0:
                for y in range(p0.y + 1, p1.y):
                    t = (y - p0.y) / dy
                    if t > 0 and t < 1:
                        t_values.append(t)
            else:
                for y in range(p0.y - 1, p1.y, -1):
                    t = (y - p0.y) / dy
                    if t > 0 and t < 1:
                        t_values.append(t)

        return self._segment_intervals_are_on_road(p0, p1, t_values)

    def first_invalid_point_on_segment(self, p0: Vertex, p1: Vertex):
        # Used after crashes to find roughly where the car left the track.
        dx = p1.x - p0.x
        dy = p1.y - p0.y
        if dx == 0 and dy == 0:
            if self._point_has_road(p0.x, p0.y):
                return None
            return (float(p0.x), float(p0.y))

        t_values = self._collect_t_values(p0, p1)
        t_values.sort()

        epsilon = 0.0000001
        for index in range(len(t_values) - 1):
            t0 = t_values[index]
            t1 = t_values[index + 1]
            if t1 - t0 > epsilon:
                t_mid = (t0 + t1) * 0.5
                x_mid = p0.x + dx * t_mid
                y_mid = p0.y + dy * t_mid
                if not self._sample_point_is_on_road(x_mid, y_mid):
                    x_exit = p0.x + dx * t0
                    y_exit = p0.y + dy * t0
                    return (x_exit, y_exit)

        return None

    def finish_vertex_for_segment(self, p0: Vertex, p1: Vertex):
        point = self._finish_intersection_point(p0, p1)
        if point is None:
            return None
        return self._finish_vertex_from_point(point[0], point[1])

    def nearest_inside_vertex(self, point: Vertex) -> Vertex:
        return self.nearest_inside_vertex_from_point(float(point.x), float(point.y))

    def nearest_inside_vertex_from_point(self, x: float, y: float) -> Vertex:
        # After a crash we "snap" the car back to the nearest legal vertex.
        min_dist_sq = None
        candidates: List[Vertex] = []

        for vertex_x in range(self.width + 1):
            for vertex_y in range(self.height + 1):
                if self._vertex_is_inside(vertex_x, vertex_y):
                    dx = vertex_x - x
                    dy = vertex_y - y
                    dist_sq = dx * dx + dy * dy
                    if min_dist_sq is None or dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        candidates = [Vertex(vertex_x, vertex_y)]
                    elif dist_sq == min_dist_sq:
                        candidates.append(Vertex(vertex_x, vertex_y))

        if candidates:
            index = random.randint(0, len(candidates) - 1)
            return candidates[index]

        return Vertex(int(round(x)), int(round(y)))

    def segment_crosses_finish(self, p0: Vertex, p1: Vertex) -> bool:
        return self._finish_intersection_point(p0, p1) is not None

    def _finish_intersection_point(self, p0: Vertex, p1: Vertex):
        # Handles both vertical and horizontal finish lines.
        fx0 = self.finish_line.start.x
        fy0 = self.finish_line.start.y
        fx1 = self.finish_line.end.x
        fy1 = self.finish_line.end.y

        if fx0 == fx1:
            if p0.x == p1.x:
                if p0.x != fx0:
                    return None
                if not self._ranges_overlap(p0.y, p1.y, fy0, fy1):
                    return None
                return (float(p1.x), float(self._clamp_int(p1.y, fy0, fy1)))

            t = (fx0 - p0.x) / (p1.x - p0.x)
            if t < 0 or t > 1:
                return None
            y = p0.y + (p1.y - p0.y) * t
            if not self._value_in_range(y, fy0, fy1):
                return None
            return (float(fx0), float(y))

        if p0.y == p1.y:
            if p0.y != fy0:
                return None
            if not self._ranges_overlap(p0.x, p1.x, fx0, fx1):
                return None
            return (float(self._clamp_int(p1.x, fx0, fx1)), float(p1.y))

        t = (fy0 - p0.y) / (p1.y - p0.y)
        if t < 0 or t > 1:
            return None
        x = p0.x + (p1.x - p0.x) * t
        if not self._value_in_range(x, fx0, fx1):
            return None
        return (float(x), float(fy0))

    def _finish_vertex_from_point(self, x: float, y: float) -> Vertex:
        fx0 = self.finish_line.start.x
        fy0 = self.finish_line.start.y
        fx1 = self.finish_line.end.x
        fy1 = self.finish_line.end.y

        if fx0 == fx1:
            vertex_y = int(round(y))
            vertex_y = self._clamp_int(vertex_y, fy0, fy1)
            return Vertex(fx0, vertex_y)

        vertex_x = int(round(x))
        vertex_x = self._clamp_int(vertex_x, fx0, fx1)
        return Vertex(vertex_x, fy0)

    def _sample_point_is_on_road(self, x: float, y: float) -> bool:
        # A point is considered road if any touching cell is road (boundary inclusive).
        if x < 0 or y < 0 or x > self.width or y > self.height:
            return False

        epsilon = 0.000001
        base_x = int(x)
        base_y = int(y)

        candidates_x: List[int] = []
        candidates_y: List[int] = []

        candidates_x.append(base_x)
        if abs(x - round(x)) < epsilon:
            candidates_x.append(base_x - 1)

        candidates_y.append(base_y)
        if abs(y - round(y)) < epsilon:
            candidates_y.append(base_y - 1)

        for cx in candidates_x:
            for cy in candidates_y:
                if self._cell_is_road(cx, cy):
                    return True

        return False

    def _collect_t_values(self, p0: Vertex, p1: Vertex) -> List[float]:
        t_values: List[float] = []
        t_values.append(0.0)
        t_values.append(1.0)

        dx = p1.x - p0.x
        dy = p1.y - p0.y

        if dx != 0:
            if dx > 0:
                for x in range(p0.x + 1, p1.x):
                    t = (x - p0.x) / dx
                    if t > 0 and t < 1:
                        t_values.append(t)
            else:
                for x in range(p0.x - 1, p1.x, -1):
                    t = (x - p0.x) / dx
                    if t > 0 and t < 1:
                        t_values.append(t)

        if dy != 0:
            if dy > 0:
                for y in range(p0.y + 1, p1.y):
                    t = (y - p0.y) / dy
                    if t > 0 and t < 1:
                        t_values.append(t)
            else:
                for y in range(p0.y - 1, p1.y, -1):
                    t = (y - p0.y) / dy
                    if t > 0 and t < 1:
                        t_values.append(t)

        return t_values

    def _segment_intervals_are_on_road(self, p0: Vertex, p1: Vertex, t_values: List[float]) -> bool:
        dx = p1.x - p0.x
        dy = p1.y - p0.y
        t_values.sort()

        epsilon = 0.0000001
        for index in range(len(t_values) - 1):
            t0 = t_values[index]
            t1 = t_values[index + 1]
            if t1 - t0 > epsilon:
                t_mid = (t0 + t1) * 0.5
                x_mid = p0.x + dx * t_mid
                y_mid = p0.y + dy * t_mid
                if not self._sample_point_is_on_road(x_mid, y_mid):
                    return False

        return True

    def _cell_is_road(self, cell_x: int, cell_y: int) -> bool:
        if cell_x < 0 or cell_x >= self.width:
            return False
        if cell_y < 0 or cell_y >= self.height:
            return False
        return self.road_mask[cell_x][cell_y]

    def _vertex_is_inside(self, vertex_x: int, vertex_y: int) -> bool:
        # A vertex is inside if any adjacent cell is road.
        for cell_x in range(vertex_x - 1, vertex_x + 1):
            for cell_y in range(vertex_y - 1, vertex_y + 1):
                if self._cell_is_road(cell_x, cell_y):
                    return True
        return False

    def _point_has_road(self, x: int, y: int) -> bool:
        return self._sample_point_is_on_road(float(x), float(y))

    def _value_in_range(self, value: float, a: int, b: int) -> bool:
        low = a
        high = b
        if low > high:
            low = b
            high = a
        return value >= low and value <= high

    def _ranges_overlap(self, a0: int, a1: int, b0: int, b1: int) -> bool:
        low_a = a0
        high_a = a1
        if low_a > high_a:
            low_a = a1
            high_a = a0
        low_b = b0
        high_b = b1
        if low_b > high_b:
            low_b = b1
            high_b = b0
        return high_a >= low_b and high_b >= low_a

    def _clamp_int(self, value: int, a: int, b: int) -> int:
        low = a
        high = b
        if low > high:
            low = b
            high = a
        if value < low:
            return low
        if value > high:
            return high
        return value

class GameState:
    def __init__(self, track: Track, cars: List[Car]):
        # Global mutable state for one full game session.
        self.track = track
        self.cars = cars
        self.current_player_idx = 0  # Index of the current player
        self.finished = False  # Whether the game is finished
        self.winners: List[int] = []  # List of winner IDs
        self.finish_triggered = False
        self.finish_after_player_idx = None
        self.performance = None

    def __repr__(self):
        return f"GameState(current_player_idx={self.current_player_idx}, finished={self.finished}, winners={self.winners})"

    def next_player(self):
        # Advance to the next player
        self.current_player_idx = (self.current_player_idx + 1) % len(self.cars)

    def check_game_finished(self):
        # Check if any car would cross the finish line on its current segment.
        winners: List[int] = []
        for car in self.cars:
            next_pos = car.pos + car.vel
            if self.track.segment_crosses_finish(car.pos, next_pos):
                winners.append(car.id)

        if winners:
            self.winners = winners
            self.finish_triggered = True
            self.finish_after_player_idx = self.current_player_idx

def create_cars_for_track(track: Track, players: int) -> List[Car]:
    # Start order is randomized so scripts do not always get the same starting slot.
    start_positions: List[Vertex] = list(track.start_vertices)

    _shuffle_vertices(start_positions)

    count = players
    if count > len(start_positions):
        count = len(start_positions)

    names = _generate_unique_names(count)
    cars: List[Car] = []
    for index in range(count):
        cars.append(Car(index, names[index], start_positions[index], Vector2i(0, 0)))
    return cars

def _shuffle_vertices(vertices: List[Vertex]):
    for i in range(len(vertices) - 1, 0, -1):
        j = random.randint(0, i)
        temp = vertices[i]
        vertices[i] = vertices[j]
        vertices[j] = temp

def _generate_unique_names(count: int) -> List[str]:
    adjectives = _ADJECTIVES.copy()
    nouns = _NOUNS.copy()
    random.shuffle(adjectives)
    random.shuffle(nouns)

    names = []
    for i in range(count):
        names.append(adjectives[i] + " " + nouns[i])

    return names
