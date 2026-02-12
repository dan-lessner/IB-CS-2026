from simulation.game_state import Vertex, Vector2i, GameState


class MoveOption:
    def __init__(self, target: Vertex, acceleration: Vector2i, valid: bool):
        self.target = target
        self.acceleration = acceleration
        self.valid = valid


def get_move_options(game_state: GameState, car_id: int):
    options = []
    car = game_state.cars[car_id]

    if car.penalty_turns_left > 0:
        options.append(MoveOption(car.pos, Vector2i(0, 0), True))
        return options

    ax = -1
    while ax <= 1:
        ay = -1
        while ay <= 1:
            new_vx = car.vel.vx + ax
            new_vy = car.vel.vy + ay
            target_x = car.pos.x + new_vx
            target_y = car.pos.y + new_vy
            target_vertex = Vertex(target_x, target_y)
            finish_vertex = game_state.track.finish_vertex_for_segment(car.pos, target_vertex)

            if finish_vertex is not None:
                target_x = finish_vertex.x
                target_y = finish_vertex.y
                segment_valid = game_state.track.segment_is_valid(car.pos, finish_vertex)
                target_valid = segment_valid and (not _target_is_occupied(game_state, car_id, target_x, target_y))
                if not _target_already_listed(options, target_x, target_y):
                    options.append(MoveOption(Vertex(target_x, target_y), Vector2i(ax, ay), target_valid))
            else:
                if _target_in_bounds(game_state, target_x, target_y):
                    segment_valid = game_state.track.segment_is_valid(car.pos, target_vertex)
                    target_valid = segment_valid and (not _target_is_occupied(game_state, car_id, target_x, target_y))
                    options.append(MoveOption(target_vertex, Vector2i(ax, ay), target_valid))

            ay += 1
        ax += 1

    if len(options) == 0:
        options.append(MoveOption(car.pos, Vector2i(0, 0), True))

    return options


def get_allowed_targets(options):
    allowed = []
    index = 0
    while index < len(options):
        option = options[index]
        if option.valid:
            allowed.append(option.target)
        index += 1
    return allowed


def get_all_targets(options):
    targets = []
    index = 0
    while index < len(options):
        targets.append(options[index].target)
        index += 1
    return targets


def get_ordered_targets_and_validity(game_state, car_id: int):
    # Return a fixed-order list of 9 vertices (ax,ay from -1..1 nested)
    # and a corresponding 9-element boolean list indicating validity.
    car = game_state.cars[car_id]

    # If car is penalized, only allow staying in place
    if car.penalty_turns_left > 0:
        return [car.pos], [True]

    targets = []
    validity = []

    ax = -1
    while ax <= 1:
        ay = -1
        while ay <= 1:
            new_vx = car.vel.vx + ax
            new_vy = car.vel.vy + ay
            target_x = car.pos.x + new_vx
            target_y = car.pos.y + new_vy
            target_vertex = Vertex(target_x, target_y)
            finish_vertex = game_state.track.finish_vertex_for_segment(car.pos, target_vertex)

            if finish_vertex is not None:
                target = finish_vertex
                segment_valid = game_state.track.segment_is_valid(car.pos, finish_vertex)
            else:
                target = target_vertex
                if not _target_in_bounds(game_state, target.x, target.y):
                    segment_valid = False
                else:
                    segment_valid = game_state.track.segment_is_valid(car.pos, target)

            occupied = _target_is_occupied(game_state, car_id, target.x, target.y)
            valid = segment_valid and (not occupied)

            targets.append(target)
            validity.append(valid)

            ay += 1
        ax += 1

    # If none are valid (collision), return only current position marked valid
    any_valid = False
    idx = 0
    while idx < len(validity):
        if validity[idx]:
            any_valid = True
            break
        idx += 1

    if not any_valid:
        return [car.pos], [True]

    return targets, validity


def find_option_for_target(options, target: Vertex):
    index = 0
    while index < len(options):
        option = options[index]
        if option.target.x == target.x and option.target.y == target.y:
            return option
        index += 1
    return None


def _target_is_occupied(game_state: GameState, car_id: int, x: int, y: int) -> bool:
    index = 0
    while index < len(game_state.cars):
        if index != car_id:
            other = game_state.cars[index]
            if other.pos.x == x and other.pos.y == y:
                return True
        index += 1
    return False


def _target_already_listed(options, x: int, y: int) -> bool:
    index = 0
    while index < len(options):
        option = options[index]
        if option.target.x == x and option.target.y == y:
            return True
        index += 1
    return False


def _target_in_bounds(game_state: GameState, x: int, y: int) -> bool:
    if x < 0 or x > game_state.track.width:
        return False
    if y < 0 or y > game_state.track.height:
        return False
    return True
