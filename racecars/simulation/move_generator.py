"""Generate all legal/illegal move targets for the current car.

UI and drivers use this to see what choices are available on a turn.
"""

from simulation.game_state import Vertex, Vector2i, GameState


def get_ordered_targets_and_validity(game_state: GameState, car_id: int):
    # Returns fixed-order targets so student scripts can map indices to accelerations.
    car = game_state.cars[car_id]

    # If car is penalized, only allow staying in place
    if car.penalty > 0:
        return [car.pos], [True]

    targets = []
    validity = []

    for ax in [-1, 0, 1]:
        for ay in [-1, 0, 1]:
            acceleration = Vector2i(ax, ay)
            new_velocity = car.vel + acceleration
            target_vertex = car.pos + new_velocity
            finish_vertex = game_state.track.finish_vertex_for_segment(car.pos, target_vertex)

            if finish_vertex is not None:
                target = finish_vertex
                segment_valid = game_state.track.segment_is_valid(car.pos, finish_vertex)
            else:
                target = target_vertex
                if not _target_in_bounds(game_state, target):
                    segment_valid = False
                else:
                    segment_valid = game_state.track.segment_is_valid(car.pos, target)

            occupied = _target_is_occupied(game_state, car_id, target)
            valid = segment_valid and (not occupied)

            targets.append(target)
            validity.append(valid)

    if len(targets) == 0:
        print(game_state)
        raise RuntimeError(
            "No targets were generated for the current turn. "
            "This should be impossible and indicates a move generation bug."
        )

    return targets, validity


def _target_is_occupied(game_state: GameState, this_car_id: int, target: Vertex) -> bool:
    for index in range(len(game_state.cars)):
        if index != this_car_id:
            if game_state.cars[index].pos == target:
                return True
    return False


def _target_in_bounds(game_state: GameState, target: Vertex) -> bool:
    if target.x < 0 or target.x > game_state.track.width:
        return False
    if target.y < 0 or target.y > game_state.track.height:
        return False
    return True
