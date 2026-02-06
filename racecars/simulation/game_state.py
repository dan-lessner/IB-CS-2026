from typing import List, Tuple
import random

_ADJECTIVES = [
    "Red", "Blue", "Green", "Yellow", "Silver", "Black",
    "Swift", "Brave", "Wild", "Mighty", "Fierce", "Lucky"
]

_NOUNS = [
    "Comet", "Falcon", "Tiger", "Eagle", "Rocket", "Panther",
    "Wolf", "Viper", "Storm", "Blaze", "Arrow", "Bolt"
]

class Vertex:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vertex(x={self.x}, y={self.y})"

class Vector2i:
    def __init__(self, vx: int, vy: int):
        self.vx = vx
        self.vy = vy

    def __repr__(self):
        return f"Vector2i(vx={self.vx}, vy={self.vy})"

class Segment:
    def __init__(self, start: Vertex, end: Vertex):
        self.start = start
        self.end = end

    def __repr__(self):
        return f"Segment(start={self.start}, end={self.end})"

class Car:
    def __init__(self, car_id: int, name: str, pos: Vertex, vel: Vector2i):
        self.id = car_id
        self.name = name
        self.pos = pos
        self.vel = vel  # Velocity vector
        self.penalty_turns_left = 0  # Number of penalty turns remaining
        self.path: List[Segment] = []  # Path history for replay/logging
        self.trail: List[Tuple[int, int]] = []  # Initialize trail as an empty list
        self.driver = None

    def __repr__(self):
        return f"Car(id={self.id}, name={self.name}, pos={self.pos}, vel={self.vel}, penalty_turns_left={self.penalty_turns_left})"

    def SetDriver(self, driver):
        self.driver = driver

    def PickMove(self, world, allowed_moves):
        if self.driver is None:
            return None
        return self.driver.PickMove(self, world, allowed_moves)

class Track:
    def __init__(self, width: int, height: int, road_mask: List[List[bool]], start_vertices: List[Vertex], finish_line: Segment):
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
        # Supercover: check each interval between grid crossings.
        dx = p1.x - p0.x
        dy = p1.y - p0.y
        if dx == 0 and dy == 0:
            return self._point_has_road(p0.x, p0.y)

        t_values = self._collect_t_values(p0, p1)

        if dx != 0:
            if dx > 0:
                x = p0.x + 1
                while x < p1.x:
                    t = (x - p0.x) / dx
                    if t > 0 and t < 1:
                        t_values.append(t)
                    x += 1
            else:
                x = p0.x - 1
                while x > p1.x:
                    t = (x - p0.x) / dx
                    if t > 0 and t < 1:
                        t_values.append(t)
                    x -= 1

        if dy != 0:
            if dy > 0:
                y = p0.y + 1
                while y < p1.y:
                    t = (y - p0.y) / dy
                    if t > 0 and t < 1:
                        t_values.append(t)
                    y += 1
            else:
                y = p0.y - 1
                while y > p1.y:
                    t = (y - p0.y) / dy
                    if t > 0 and t < 1:
                        t_values.append(t)
                    y -= 1

        return self._segment_intervals_are_on_road(p0, p1, t_values)

    def first_invalid_point_on_segment(self, p0: Vertex, p1: Vertex):
        dx = p1.x - p0.x
        dy = p1.y - p0.y
        if dx == 0 and dy == 0:
            if self._point_has_road(p0.x, p0.y):
                return None
            return (float(p0.x), float(p0.y))

        t_values = self._collect_t_values(p0, p1)
        t_values.sort()

        index = 0
        epsilon = 0.0000001
        while index < len(t_values) - 1:
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
            index += 1

        return None

    def finish_vertex_for_segment(self, p0: Vertex, p1: Vertex):
        point = self._finish_intersection_point(p0, p1)
        if point is None:
            return None
        return self._finish_vertex_from_point(point[0], point[1])

    def nearest_inside_vertex(self, point: Vertex) -> Vertex:
        return self.nearest_inside_vertex_from_point(float(point.x), float(point.y))

    def nearest_inside_vertex_from_point(self, x: float, y: float) -> Vertex:
        # Find the nearest vertex that is inside the track.
        min_dist_sq = None
        candidates: List[Vertex] = []

        vx = 0
        while vx <= self.width:
            vy = 0
            while vy <= self.height:
                if self._vertex_is_inside(vx, vy):
                    dx = vx - x
                    dy = vy - y
                    dist_sq = dx * dx + dy * dy
                    if min_dist_sq is None or dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        candidates = [Vertex(vx, vy)]
                    elif dist_sq == min_dist_sq:
                        candidates.append(Vertex(vx, vy))
                vy += 1
            vx += 1

        if candidates:
            index = random.randint(0, len(candidates) - 1)
            return candidates[index]

        return Vertex(int(round(x)), int(round(y)))

    def segment_crosses_finish(self, p0: Vertex, p1: Vertex) -> bool:
        return self._finish_intersection_point(p0, p1) is not None

    def _finish_intersection_point(self, p0: Vertex, p1: Vertex):
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
            vy = int(round(y))
            vy = self._clamp_int(vy, fy0, fy1)
            return Vertex(fx0, vy)

        vx = int(round(x))
        vx = self._clamp_int(vx, fx0, fx1)
        return Vertex(vx, fy0)

    def _sample_point_is_on_road(self, x: float, y: float) -> bool:
        # Determine whether the point lies on any road cell (boundary inclusive).
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

        cx_index = 0
        while cx_index < len(candidates_x):
            cy_index = 0
            while cy_index < len(candidates_y):
                cx = candidates_x[cx_index]
                cy = candidates_y[cy_index]
                if self._cell_is_road(cx, cy):
                    return True
                cy_index += 1
            cx_index += 1

        return False

    def _collect_t_values(self, p0: Vertex, p1: Vertex) -> List[float]:
        t_values: List[float] = []
        t_values.append(0.0)
        t_values.append(1.0)

        dx = p1.x - p0.x
        dy = p1.y - p0.y

        if dx != 0:
            if dx > 0:
                x = p0.x + 1
                while x < p1.x:
                    t = (x - p0.x) / dx
                    if t > 0 and t < 1:
                        t_values.append(t)
                    x += 1
            else:
                x = p0.x - 1
                while x > p1.x:
                    t = (x - p0.x) / dx
                    if t > 0 and t < 1:
                        t_values.append(t)
                    x -= 1

        if dy != 0:
            if dy > 0:
                y = p0.y + 1
                while y < p1.y:
                    t = (y - p0.y) / dy
                    if t > 0 and t < 1:
                        t_values.append(t)
                    y += 1
            else:
                y = p0.y - 1
                while y > p1.y:
                    t = (y - p0.y) / dy
                    if t > 0 and t < 1:
                        t_values.append(t)
                    y -= 1

        return t_values

    def _segment_intervals_are_on_road(self, p0: Vertex, p1: Vertex, t_values: List[float]) -> bool:
        dx = p1.x - p0.x
        dy = p1.y - p0.y
        t_values.sort()

        index = 0
        epsilon = 0.0000001
        while index < len(t_values) - 1:
            t0 = t_values[index]
            t1 = t_values[index + 1]
            if t1 - t0 > epsilon:
                t_mid = (t0 + t1) * 0.5
                x_mid = p0.x + dx * t_mid
                y_mid = p0.y + dy * t_mid
                if not self._sample_point_is_on_road(x_mid, y_mid):
                    return False
            index += 1

        return True

    def _cell_is_road(self, cell_x: int, cell_y: int) -> bool:
        if cell_x < 0 or cell_x >= self.width:
            return False
        if cell_y < 0 or cell_y >= self.height:
            return False
        return self.road_mask[cell_x][cell_y]

    def _vertex_is_inside(self, vx: int, vy: int) -> bool:
        # A vertex is inside if any adjacent cell is road.
        cell_x = vx - 1
        while cell_x <= vx:
            cell_y = vy - 1
            while cell_y <= vy:
                if self._cell_is_road(cell_x, cell_y):
                    return True
                cell_y += 1
            cell_x += 1
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
        index = 0
        while index < len(self.cars):
            car = self.cars[index]
            next_pos = Vertex(car.pos.x + car.vel.vx, car.pos.y + car.vel.vy)
            if self.track.segment_crosses_finish(car.pos, next_pos):
                winners.append(car.id)
            index += 1

        if winners:
            self.winners = winners
            self.finish_triggered = True
            self.finish_after_player_idx = self.current_player_idx

def create_cars_for_track(track: Track, players: int) -> List[Car]:
    # Shuffle start positions and assign random names.
    start_positions: List[Vertex] = []
    index = 0
    while index < len(track.start_vertices):
        start_positions.append(track.start_vertices[index])
        index += 1

    _shuffle_vertices(start_positions)

    count = players
    if count > len(start_positions):
        count = len(start_positions)

    names = _generate_unique_names(count)
    cars: List[Car] = []
    index = 0
    while index < count:
        cars.append(Car(index, names[index], start_positions[index], Vector2i(0, 0)))
        index += 1
    return cars

def _shuffle_vertices(vertices: List[Vertex]):
    i = len(vertices) - 1
    while i > 0:
        j = random.randint(0, i)
        temp = vertices[i]
        vertices[i] = vertices[j]
        vertices[j] = temp
        i -= 1

def _generate_unique_names(count: int) -> List[str]:
    names: List[str] = []
    tries = 0
    while len(names) < count and tries < count * 20:
        name = _random_car_name()
        if not _name_in_list(name, names):
            names.append(name)
        tries += 1

    suffix = 1
    while len(names) < count:
        base = _random_car_name()
        name = base + " " + str(suffix)
        suffix += 1
        if not _name_in_list(name, names):
            names.append(name)

    return names

def _random_car_name() -> str:
    adj_index = random.randint(0, len(_ADJECTIVES) - 1)
    noun_index = random.randint(0, len(_NOUNS) - 1)
    return _ADJECTIVES[adj_index] + " " + _NOUNS[noun_index]

def _name_in_list(name: str, names: List[str]) -> bool:
    index = 0
    while index < len(names):
        if names[index] == name:
            return True
        index += 1
    return False
