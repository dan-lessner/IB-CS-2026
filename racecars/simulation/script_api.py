from simulation.game_state import Vertex, Vector2i


class AutoAuto:
    def GetName(self) -> str:
        return ""

    def PickMove(self, auto, world, targets, validity):
        # Default implementation: pick first valid target
        if targets is None or validity is None:
            return None
        if len(targets) == 0:
            return None
        index = 0
        while index < len(targets):
            if index < len(validity) and validity[index]:
                return targets[index]
            index += 1
        return None


class CarInfo:
    def __init__(self, car_id: int, name: str, pos: Vertex, vel: Vector2i):
        self.id = car_id
        self.name = name
        self.pos = pos
        self.vel = vel


class WorldState:
    def __init__(self, road, start_vertices, finish_vertices, cars):
        self.road = road
        self.start_vertices = start_vertices
        self.finish_vertices = finish_vertices
        self.cars = cars


def build_world_state(game_state):
    track = game_state.track
    finish_vertices = _finish_vertices_from_line(track.finish_line)
    cars = []

    index = 0
    while index < len(game_state.cars):
        car = game_state.cars[index]
        car_info = CarInfo(car.id, car.name, Vertex(car.pos.x, car.pos.y), Vector2i(car.vel.vx, car.vel.vy))
        cars.append(car_info)
        index += 1

    start_vertices = _copy_vertices(track.start_vertices)
    return WorldState(track.road_mask, start_vertices, finish_vertices, cars)


def _copy_vertices(vertices):
    result = []
    index = 0
    while index < len(vertices):
        v = vertices[index]
        result.append(Vertex(v.x, v.y))
        index += 1
    return result


def _finish_vertices_from_line(line):
    vertices = []
    start = line.start
    end = line.end

    if start.x == end.x:
        x = start.x
        y = start.y
        step = 1
        if end.y < start.y:
            step = -1
        while True:
            vertices.append(Vertex(x, y))
            if y == end.y:
                break
            y = y + step
        return vertices

    y = start.y
    x = start.x
    step = 1
    if end.x < start.x:
        step = -1
    while True:
        vertices.append(Vertex(x, y))
        if x == end.x:
            break
        x = x + step
    return vertices
