"""Apply one player's chosen action and update the shared game state."""

from simulation.game_state import GameState, Vertex, Vector2i, Segment

class TurnLogic:
    @staticmethod
    def apply_move(game_state: GameState, car_id: int, intended_target: Vertex):
        if game_state.finished:
            return

        car = game_state.cars[car_id]

        if car.penalty > 0:
            # Crash penalty consumes turns before the car can move again.
            car.penalty -= 1
            TurnLogic._advance_turn_and_finalize_if_needed(game_state)
            return

        old_position = car.pos

        # Velocity is derived from target delta, not from acceleration.
        new_velocity = intended_target - old_position
        intended_position = old_position + new_velocity

        finish_vertex = game_state.track.finish_vertex_for_segment(old_position, intended_position)
        if finish_vertex is not None:
            # Crossing the finish line snaps movement to that line segment.
            new_position = finish_vertex
            new_velocity = new_position - old_position
        else:
            new_position = intended_position

        # Validate the move and check for collisions
        target_occupied = TurnLogic._target_is_occupied(game_state, car_id, new_position)
        segment_valid = game_state.track.segment_is_valid(old_position, new_position)

        if target_occupied or not segment_valid:
            # Collision/off-track handling: keep a crash segment and reset speed.
            exit_point = game_state.track.first_invalid_point_on_segment(old_position, new_position)
            if exit_point is None:
                collision_point = new_position
                collision_vertex = collision_point
                car.pos = game_state.track.nearest_inside_vertex(collision_point)
            else:
                collision_vertex = Vertex(int(round(exit_point[0])), int(round(exit_point[1])))
                car.pos = game_state.track.nearest_inside_vertex_from_point(exit_point[0], exit_point[1])
            if collision_vertex != old_position:
                car.path.append(Segment(old_position, collision_vertex))
            car.vel = Vector2i(0, 0)
            if TurnLogic._should_apply_penalty(game_state, target_occupied, segment_valid):
                car.penalty = TurnLogic._compute_penalty_rounds(game_state, new_velocity)
            else:
                car.penalty = 0
        else:
            # Normal move: append to replay path and keep new velocity.
            car.path.append(Segment(old_position, new_position))
            car.pos = new_position
            car.vel = new_velocity

        # Check if the car crosses the finish line (only on a valid move)
        crossed_finish = False
        if not target_occupied and segment_valid:
            if game_state.track.segment_crosses_finish(old_position, new_position):
                crossed_finish = True

        if crossed_finish:
            # Game ends only after everyone had the same number of turns.
            if not TurnLogic._winner_exists(game_state, car.id):
                game_state.winners.append(car.id)
            if not game_state.finish_triggered:
                game_state.finish_triggered = True
                game_state.finish_after_player_idx = game_state.current_player_idx

        TurnLogic._advance_turn_and_finalize_if_needed(game_state)

    @staticmethod
    def _target_is_occupied(game_state: GameState, car_id: int, target: Vertex) -> bool:
        for index in range(len(game_state.cars)):
            if index != car_id:
                other = game_state.cars[index]
                if other.pos == target:
                    return True
        return False

    @staticmethod
    def _winner_exists(game_state: GameState, car_id: int) -> bool:
        for winner_id in game_state.winners:
            if winner_id == car_id:
                return True
        return False

    @staticmethod
    def _advance_turn_and_finalize_if_needed(game_state: GameState):
        game_state.next_player()
        if game_state.finish_triggered:
            if game_state.current_player_idx == game_state.finish_after_player_idx:
                game_state.finished = True

    @staticmethod
    def _should_apply_penalty(game_state: GameState, target_occupied: bool, segment_valid: bool):
        # Off-track collisions still penalize. Car-to-car penalty can be disabled.
        if not segment_valid:
            return True
        if target_occupied and game_state.car_collision_penalty_enabled:
            return True
        return False

    @staticmethod
    def _compute_penalty_rounds(game_state: GameState, collision_velocity: Vector2i):
        if game_state.penalty_mode == "velocity_plus":
            base_speed = TurnLogic._velocity_size(collision_velocity)
            rounds = base_speed + game_state.penalty_value
        else:
            rounds = game_state.penalty_value
        if rounds < 0:
            rounds = 0
        return rounds

    @staticmethod
    def _velocity_size(velocity: Vector2i):
        x_size = abs(velocity.x)
        y_size = abs(velocity.y)
        if x_size >= y_size:
            return x_size
        return y_size
