import time
from simulation.game_state import GameState, Vertex
from simulation.move_generator import get_move_options, get_ordered_targets_and_validity, find_option_for_target
from simulation.turn_logic import TurnLogic
from simulation.script_api import build_world_state


class Controller:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def apply_click(self, grid_x: int, grid_y: int):
        if self.game_state.finished:
            return
        if not self.game_state.cars:
            return

        target = Vertex(grid_x, grid_y)
        car = self.game_state.cars[self.game_state.current_player_idx]
        if car.driver is None:
            return
        if hasattr(car.driver, "SetTarget"):
            car.driver.SetTarget(target)

    def update(self):
        if self.game_state.finished:
            return
        if not self.game_state.cars:
            return

        car_id = self.game_state.current_player_idx
        options = get_move_options(self.game_state, car_id)
        targets, validity = get_ordered_targets_and_validity(self.game_state, car_id)
        world = build_world_state(self.game_state)
        car = self.game_state.cars[car_id]
        tracker = self.game_state.performance
        start_time = None
        if tracker is not None and tracker.enabled:
            start_time = time.perf_counter()
        target = car.PickMove(world, targets, validity)
        if start_time is not None:
            elapsed = time.perf_counter() - start_time
            tracker.record(car_id, elapsed)

        if target is None:
            if self._driver_waits_for_click(car.driver):
                return
            option = self._center_option(options)
            if option is None:
                return
            TurnLogic.apply_move(self.game_state, car_id, option.acceleration)
            self._report_if_finished()
            return

        if not self._target_in_list(target, targets):
            TurnLogic.apply_wait_move(self.game_state, car_id)
            self._report_if_finished()
            return

        option = find_option_for_target(options, target)
        if option is None:
            TurnLogic.apply_wait_move(self.game_state, car_id)
            self._report_if_finished()
            return

        TurnLogic.apply_move(self.game_state, car_id, option.acceleration)
        self._report_if_finished()

    def get_move_options(self):
        if not self.game_state.cars:
            return []
        return get_move_options(self.game_state, self.game_state.current_player_idx)

    def _target_in_list(self, target, allowed):
        index = 0
        while index < len(allowed):
            allowed_target = allowed[index]
            if allowed_target.x == target.x and allowed_target.y == target.y:
                return True
            index += 1
        return False

    def _center_option(self, options):
        index = 0
        while index < len(options):
            option = options[index]
            if option.acceleration.vx == 0 and option.acceleration.vy == 0:
                return option
            index += 1
        if len(options) > 0:
            return options[0]
        return None

    def _driver_waits_for_click(self, driver) -> bool:
        if driver is None:
            return False
        return hasattr(driver, "SetTarget")

    def _report_if_finished(self):
        tracker = self.game_state.performance
        if tracker is None:
            return
        if not self.game_state.finished:
            return
        tracker.report_if_ready(self.game_state.cars)
