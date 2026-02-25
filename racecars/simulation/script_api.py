"""Public API objects that student Auto scripts are expected to use."""

import logging
from simulation.game_state import Vertex, Vector2i

_LOGGER = logging.getLogger("racecars.script_api")

class AutoAuto:
    def __init__(self, logger: logging.Logger = _LOGGER):
        self.logger = logger

    def GetName(self) -> str:
        return "Why do you insantiate AutoAuto? You should subclass it and override GetName and PickMove."

    def PickMove(self, auto, world, targets, validity):
        # Default implementation: pick first valid target
        if targets is None or validity is None:
            self.logger.warning("PickMove() received targets or validity as None. Returning None.")
            return None
        if len(targets) == 0:
            self.logger.warning("PickMove() received no targets. Returning None.")
            return None
        for index, target in enumerate(targets):
            if index < len(validity) and validity[index]:
                return target
        return None

class CarInfo:
    def __init__(self, car_id: int, name: str, pos: Vertex, vel: Vector2i):
        self.id = car_id
        self.name = name
        self.pos = pos
        self.vel = vel


class WorldState:
    def __init__(self, road, start_vertices, finish_vertices, cars):
        # Snapshot passed to scripts so they can plan their next target.
        self.road = road
        self.start_vertices = start_vertices
        self.finish_vertices = finish_vertices
        self.cars = cars


def build_world_state(game_state):
    # Build a copy-only view of the world to avoid scripts mutating engine internals.
    track = game_state.track
    finish_vertices = _finish_vertices_from_line(track.finish_line)
    cars = []

    for car in game_state.cars:
        car_info = CarInfo(car.id, car.name, Vertex(car.pos.x, car.pos.y), Vector2i(car.vel.x, car.vel.y))
        cars.append(car_info)

    start_vertices = _copy_vertices(track.start_vertices)
    return WorldState(track.road_mask, start_vertices, finish_vertices, cars)


def _copy_vertices(vertices):
    return [Vertex(v.x, v.y) for v in vertices]


def _finish_vertices_from_line(line):
    vertices = []
    start = line.start
    end = line.end

    if start.x == end.x:
        x = start.x
        step = 1 if end.y >= start.y else -1
        for y in range(start.y, end.y + step, step):
            vertices.append(Vertex(x, y))
        return vertices

    y = start.y
    step = 1 if end.x >= start.x else -1
    for x in range(start.x, end.x + step, step):
        vertices.append(Vertex(x, y))
    return vertices
