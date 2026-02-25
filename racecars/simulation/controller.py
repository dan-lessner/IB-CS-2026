"""Bridge between drivers and turn logic.

Each frame it asks the current driver for a target and applies the chosen move.
"""

import logging
import time
from simulation.game_state import GameState, Vertex
from simulation.move_generator import get_ordered_targets_and_validity
from simulation.turn_logic import TurnLogic
from simulation.script_api import build_world_state

_LOGGER = logging.getLogger("racecars.controller")


class Controller:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def apply_click(self, grid_x: int, grid_y: int):
        # Clicks are forwarded only to drivers that support manual targeting.
        if self.game_state.finished:
            return
        if not self.game_state.cars:
            return

        target = Vertex(grid_x, grid_y)
        car = self.game_state.cars[self.game_state.current_player_idx]
        if car.driver is None:
            car.logger.warning("Click ignored because current car has no driver.")
            return
        if hasattr(car.driver, "SetTarget"):
            car.driver.SetTarget(target)

    def update(self):
        # Core turn loop for one car: generate targets, ask driver, apply result.
        if self.game_state.finished:
            return
        if not self.game_state.cars:
            return

        car_id = self.game_state.current_player_idx
        targets, validity = self.get_targets_and_validity()
        if len(targets) == 0:
            raise RuntimeError("No targets generated for current turn.", car)
        world = build_world_state(self.game_state)
        car = self.game_state.cars[car_id]
        tracker = self.game_state.performance
        start_time = None
        if tracker is not None and tracker.enabled:
            start_time = time.perf_counter()
        target = None
        pickmove_failed = False
        try:
            target = car.PickMove(world, targets, validity)
            if not isinstance(target, Vertex):
                raise ValueError(f"PickMove() returned an invalid target of type {type(target).__name__}.")
        except Exception as ex:
            pickmove_failed = True
            car.logger.exception(
                "PickMove() raised an exception (%s: %s). Applying safe fallback move.",
                type(ex).__name__,
                ex
            )
        if start_time is not None:
            elapsed = time.perf_counter() - start_time
            tracker.record(car_id, elapsed)

        if pickmove_failed:
            target = self._drifting_target(car_id)

        if target is None:
            # Manual players can return None while waiting for a click.
            if self._driver_waits_for_click(car.driver):
                return

        TurnLogic.apply_move(self.game_state, car_id, target)
        self._report_if_finished()

    def get_targets_and_validity(self):
        if not self.game_state.cars:
            return [], []
        targets, validity = get_ordered_targets_and_validity(
            self.game_state,
            self.game_state.current_player_idx
        )
        if len(targets) == 0:
            print(self.game_state)
            raise RuntimeError(
                "No targets were generated for the current turn. "
                "This should be impossible and indicates a move generation bug."
            )
        return targets, validity

    def _target_in_list(self, target, allowed):
        for allowed_target in allowed:
            if allowed_target == target:
                return True
        return False

    def _drifting_target(self, car_id):
        # Ordered targets map ax=-1..1, ay=-1..1, so center is index 4.
        # But we generate it new, in case something is wrong with the provided list
        car = self.game_state.cars[car_id]
        return car.pos + car.vel
    
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


