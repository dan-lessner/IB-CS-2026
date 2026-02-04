from simulation.game_state import GameState, Vertex, Vector2i, Segment

class TurnLogic:
    @staticmethod
    def apply_move(game_state: GameState, car_id: int, acceleration: Vector2i):
        if game_state.finished:
            return

        car = game_state.cars[car_id]

        if car.penalty_turns_left > 0:
            car.penalty_turns_left -= 1
            game_state.next_player()
            return

        # Calculate new velocity
        new_velocity = Vector2i(car.vel.vx + acceleration.vx, car.vel.vy + acceleration.vy)

        # Calculate intended position
        intended_position = Vertex(car.pos.x + new_velocity.vx, car.pos.y + new_velocity.vy)

        old_position = car.pos

        finish_vertex = game_state.track.finish_vertex_for_segment(old_position, intended_position)
        if finish_vertex is not None:
            new_position = finish_vertex
            new_velocity = Vector2i(new_position.x - old_position.x, new_position.y - old_position.y)
        else:
            new_position = intended_position

        # Validate the move and check for collisions
        target_occupied = TurnLogic._target_is_occupied(game_state, car_id, new_position)
        segment_valid = game_state.track.segment_is_valid(old_position, new_position)

        if target_occupied or not segment_valid:
            # Handle collision or off-track move
            exit_point = game_state.track.first_invalid_point_on_segment(old_position, new_position)
            if exit_point is None:
                collision_point = new_position
                collision_vertex = Vertex(collision_point.x, collision_point.y)
                car.pos = game_state.track.nearest_inside_vertex(collision_point)
            else:
                collision_vertex = Vertex(int(round(exit_point[0])), int(round(exit_point[1])))
                car.pos = game_state.track.nearest_inside_vertex_from_point(exit_point[0], exit_point[1])
            if not (collision_vertex.x == old_position.x and collision_vertex.y == old_position.y):
                car.path.append(Segment(old_position, collision_vertex))
            car.vel = Vector2i(0, 0)
            car.penalty_turns_left = 2
        else:
            # Apply the move
            car.path.append(Segment(old_position, new_position))
            car.pos = new_position
            car.vel = new_velocity

        # Check if the car crosses the finish line (only on a valid move)
        crossed_finish = False
        if not target_occupied and segment_valid:
            if game_state.track.segment_crosses_finish(old_position, new_position):
                crossed_finish = True

        if crossed_finish:
            if not TurnLogic._winner_exists(game_state, car.id):
                game_state.winners.append(car.id)
            if not game_state.finish_triggered:
                game_state.finish_triggered = True
                game_state.finish_after_player_idx = game_state.current_player_idx

        # Update the current player index
        game_state.next_player()

        if game_state.finish_triggered:
            if game_state.current_player_idx == game_state.finish_after_player_idx:
                game_state.finished = True

    @staticmethod
    def apply_wait_move(game_state: GameState, car_id: int):
        if game_state.finished:
            return

        car = game_state.cars[car_id]

        if car.penalty_turns_left > 0:
            car.penalty_turns_left -= 1
            game_state.next_player()
            return

        car.vel = Vector2i(0, 0)
        game_state.next_player()

        if game_state.finish_triggered:
            if game_state.current_player_idx == game_state.finish_after_player_idx:
                game_state.finished = True

    @staticmethod
    def _target_is_occupied(game_state: GameState, car_id: int, target: Vertex) -> bool:
        index = 0
        while index < len(game_state.cars):
            if index != car_id:
                other = game_state.cars[index]
                if other.pos.x == target.x and other.pos.y == target.y:
                    return True
            index += 1
        return False

    @staticmethod
    def _winner_exists(game_state: GameState, car_id: int) -> bool:
        index = 0
        while index < len(game_state.winners):
            if game_state.winners[index] == car_id:
                return True
            index += 1
        return False
