"""Main entry point for the racecars game.

This file wires together setup, track generation, driver loading, and the UI loop.
"""

import logging
import os
import random
from typing import List
from simulation.game_state import GameState, Car, Track, Vertex
from simulation.track_generator import generate_track
from simulation.params import GameParams
from simulation.config import (
    parse_console_args,
    parse_controllers_text,
    print_basic_console_help,
    print_advanced_console_help
)
from simulation.manual_auto import MouseAuto
from simulation.script_loader import load_scripts_from_folder, load_auto_class
from simulation.performance import PerformanceTracker
from ui.logging_utils import setup_logging, sanitize_logger_name
from ui.renderer import Renderer
from ui.setup_dialog import SetupDialog
from ui.controller_dialog import ControllerDialog

_LOGGER = logging.getLogger("racecars.main")

def _filter_visible_scripts(script_infos):
    visible = []
    for info in script_infos:
        if info.name is None or info.name.lower() != "randomauto":
            visible.append(info)
    return visible

def _find_script_info(script_infos, name: str):
    if name is None:
        return None
    target = name.lower()
    target_no_ext = _strip_py_extension(target)
    for info in script_infos:
        info_name = info.name.lower()
        info_file = info.file_name.lower()
        if info_name == target or info_file == target or info_name == target_no_ext:
            return info
    return None


def _strip_py_extension(name: str) -> str:
    if name.endswith(".py"):
        return name[:-3]
    return name


def _create_cars_for_track(track: Track, players: int, controllers, script_infos) -> List[Car]:
    # Start order is randomized so scripts do not always get the same starting slot.
    start_positions = list(track.start_vertices)
    random.shuffle(start_positions)

    count = players
    if count > len(start_positions):
        count = len(start_positions)

    # generate random names
    ADJECTIVES = ["Red", "Blue", "Green", "Yellow", "Silver", "Black",
    "Swift", "Brave", "Wild", "Mighty", "Fierce", "Lucky"]
    NOUNS = ["Comet", "Falcon", "Tiger", "Eagle", "Rocket", "Panther",
    "Wolf", "Viper", "Storm", "Blaze", "Arrow", "Bolt"]
    random.shuffle(ADJECTIVES)
    random.shuffle(NOUNS)
    names = []
    for i in range(count):
        names.append(ADJECTIVES[i] + " " + NOUNS[i])

    cars: List[Car] = []
    for index in range(count):
        controller_name = "mouse"
        if index < len(controllers):
            controller_name = controllers[index]

        driver = MouseAuto()
        logger = logging.getLogger("racecars.car." + sanitize_logger_name("Mouse") + ".id_" + str(index + 1))
        if controller_name.lower() != "mouse":
            try:
                script_info = _find_script_info(script_infos, controller_name)
                if script_info is None:
                    raise ValueError("Controller '%s' was not found. Falling back to mouse for car %s." % (controller_name, index + 1))   
                auto_class = load_auto_class(script_info)
                if auto_class is None:
                    raise ValueError("Failed to load script '%s'. Falling back to mouse for car %s." % (script_info.name, index + 1))
                driver = auto_class(track)
                try:
                    name = driver.GetName()
                except Exception as ex:
                    car.logger.exception("GetName() failed for script '%s' (%s: %s). Using script file name as fallback.", script_info.name, type(ex).__name__, ex)
                    name = script_info.name
                names[index] = name
                logger = logging.getLogger("racecars.car." + sanitize_logger_name(script_info.name) + ".id_" + str(index + 1))
            except Exception as ex:
                _LOGGER.exception("Script '%s' raised during initialization (%s: %s). Falling back to mouse for car %s.", script_info.name, type(ex).__name__, ex, index + 1)

        # finally create the car        
        cars.append(Car(index, names[index], start_positions[index], driver = driver, logger = logger))

    return cars

def _print_start_instructions():
    print("Players: use --players N or players=N")
    print("Measure: use --measure")
    print("Controllers: use --controllers mouse,ScriptName")
    print("Framerate: use --framerate N or framerate=N")
    print("Skip GUI: use --no-gui")
    print("List console params: use --list-params")

def main():
    # 1) Gather parameters and available scripts.
    parsed_config = parse_console_args(GameParams())
    params = parsed_config.params
    provided_any = parsed_config.provided_any
    start_without_gui = parsed_config.start_without_gui
    list_params = parsed_config.list_params
    list_advanced_parameters = parsed_config.list_advanced_parameters
    controllers_text = parsed_config.controllers_text
    suppress_log = parsed_config.suppress_log
    log_path = parsed_config.log_path
    log_level = parsed_config.log_level

    if suppress_log:
        setup_logging(log_level, to_console=False, file_path=None)
    else:
        setup_logging(log_level, to_console=True, file_path=log_path)

    if list_params:
        print_basic_console_help()
        if list_advanced_parameters:
            print("")
            print_advanced_console_help()
        return

    if list_advanced_parameters:
        print_advanced_console_help()
        return

    scripts_folder = os.path.join(os.path.dirname(__file__), "Scripts")
    scripts = load_scripts_from_folder(scripts_folder)
    visible_scripts = _filter_visible_scripts(scripts)
    script_names_all = [info.name for info in scripts]
    script_names_default = [info.name for info in visible_scripts]

    # 2) Decide who will control each car (mouse vs script).
    controllers = parse_controllers_text(controllers_text)
    if controllers is not None and len(controllers) == 0:
        controllers = None

    if controllers is None and not provided_any and not start_without_gui and len(script_names_default) > 0:
        params.players = len(script_names_default)
        if params.players > 10:
            params.players = 10

    if controllers is not None:
        params.players = len(controllers)

    # 3) Optionally run setup dialogs for easier classroom use.
    if not start_without_gui:
        dialog = SetupDialog(params)
        params = dialog.run()
        if controllers is not None:
            params.players = len(controllers)

    if controllers is None:
        controllers = list(script_names_default[:10])
        controllers = list(controllers[:params.players])
        if len(controllers) < params.players:
            controllers.extend(["mouse"] * (params.players - len(controllers)))
        if not start_without_gui:
            options = ["Mouse"] + script_names_all
            dialog = ControllerDialog(params.players, options, controllers)
            controllers = dialog.run()
            controllers = list(controllers[:params.players])
            if len(controllers) < params.players:
                controllers.extend(["mouse"] * (params.players - len(controllers)))
        if start_without_gui:
            params.players = 2
            controllers = []
            controllers.append("mouse")
            controllers.append("mouse")

    # 4) Build the world
    # Generate a simple track
    track = generate_track(
        width=params.width-2,
        height=params.height-2,
        players=params.players,
        track_width_mean=params.track_width_mean,
        track_width_var=params.track_width_var,
        turn_density=params.turn_density,
        turn_sharpness=params.turn_sharpness,
        seed=params.seed
    )

    # add bounderies
    track.width = params.width
    track.height = params.height
    # vertical
    track.road_mask.insert(0, [False for x in range(params.height)])
    track.road_mask.append([False for x in range(params.height)])
    #horizontal
    for x in range(params.width):
        track.road_mask[x].insert(0, False)
        track.road_mask[x].append(False)

    # move start and finish lines
    track.start_line.start.x = 1
    track.start_line.end.x = 1
    for i in range(len(track.start_vertices)):
        track.start_vertices[i] = (Vertex(track.start_vertices[i].x+1, track.start_vertices[i].y))
    track.finish_line.start.x = params.width - 1
    track.finish_line.end.x = params.width - 1
    #print track.start_line.start, track.start_line.end
    # Create cars
    cars = _create_cars_for_track(track, params.players, controllers, scripts)

    # Initialize game state
    game_state = GameState(
        track=track,
        cars=cars,
        car_collision_penalty_enabled=params.car_collision_penalty_enabled,
        shuffle_turn_order_each_round=params.shuffle_turn_order_each_round,
        strict_target_check=params.strict_target_check,
        penalty_mode=params.penalty_mode,
        penalty_value=params.penalty_value
    )
    if params.measure_performance:
        log_path = os.path.join(os.path.dirname(__file__), "performance_log.csv")
        game_state.performance = PerformanceTracker(len(cars), log_path)

    # 5) Hand off to renderer; it drives the game loop until window close.
    # Start the renderer
    renderer = Renderer(game_state, framerate=params.framerate)
    _print_start_instructions()
    renderer.run()


if __name__ == "__main__":
    main()
