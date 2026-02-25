"""Main entry point for the racecars game.

This file wires together setup, track generation, driver loading, and the UI loop.
"""

from asyncio.log import logger
import logging
import os
import sys
import random
from typing import List
from simulation.game_state import GameState, Car, Track
from simulation.track_generator import generate_track
from simulation.params import GameParams
from simulation.manual_auto import MouseAuto
from simulation.script_loader import load_scripts_from_folder, load_auto_class
from simulation.performance import PerformanceTracker
from ui.logging_utils import setup_logging, sanitize_logger_name
from ui.renderer import Renderer
from ui.setup_dialog import SetupDialog
from ui.controller_dialog import ControllerDialog

_LOGGER = logging.getLogger("racecars.main")


def _is_int_string(text: str, allow_negative: bool):
    # Small helper used by both CLI parsing and setup dialogs.
    if text == "":
        return False
    index = 0
    if allow_negative and text[0] == "-":
        if len(text) == 1:
            return False
        index = 1
    for ch in text[index:]:
        if not ch.isdigit():
            return False
    return True


def _parse_arg_pair(token: str):
    if "=" not in token:
        return None, None
    parts = token.split("=", 1)
    if len(parts) != 2:
        return None, None
    key = parts[0].strip()
    value = parts[1].strip()
    key = _strip_prefix(key, "--")
    return key, value


def _strip_prefix(text: str, prefix: str) -> str:
    if not text.startswith(prefix):
        return text
    return text[len(prefix):]


def _apply_arg_value(params: GameParams, key: str, value: str):
    # Keep command-line parsing centralized so the rest of the program can trust GameParams.
    if key == "width" and _is_int_string(value, False):
        params.width = int(value)
        return
    if key == "height" and _is_int_string(value, False):
        params.height = int(value)
        return
    if key == "players" and _is_int_string(value, False):
        params.players = int(value)
        return
    if key == "track_width_mean" and _is_int_string(value, False):
        params.track_width_mean = int(value)
        return
    if key == "track_width_var" and _is_int_string(value, False):
        params.track_width_var = int(value)
        return
    if key == "turn_sharpness" and _is_int_string(value, False):
        params.turn_sharpness = int(value)
        return
    if key == "turn_density" and _is_int_string(value, False):
        params.turn_density = int(value)
        return
    if key == "seed":
        if value == "" or value == "none" or value == "None":
            params.seed = None
            return
        if _is_int_string(value, True):
            params.seed = int(value)
            return
    if key == "measure":
        if value == "1" or value.lower() == "true":
            params.measure_performance = True
            return
        if value == "0" or value.lower() == "false":
            params.measure_performance = False
            return


def _apply_console_args(default_params: GameParams):
    # Parse optional CLI overrides. If none are provided, the GUI flow is used.
    params = default_params.clone()
    args = sys.argv[1:]

    provided_any = False
    start_without_gui = False
    list_params = False
    controllers_text = None
    suppress_log = False
    log_path = None
    log_level = "INFO"
    skip_next = False
    for index, token in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        next_token = None
        has_next = index + 1 < len(args)
        if has_next:
            next_token = args[index + 1]
        if token == "--supress-log" or token == "--suppress-log":
            if has_next and not next_token.startswith("--"):
                suppress_log = _is_true_text(next_token)
                skip_next = True
            else:
                suppress_log = True
            continue
        if token == "--no-gui" or token == "--start":
            start_without_gui = True
            continue
        if token == "--measure":
            params.measure_performance = True
            provided_any = True
            continue
        if token == "--list-params" or token == "--help-params":
            list_params = True
            continue
        key, value = _parse_arg_pair(token)
        if key is not None:
            if _is_suppress_log_key(key):
                suppress_log = _is_true_text(value)
                continue
            if _is_log_path_key(key):
                log_path = value
                continue
            if _is_log_level_key(key):
                log_level = value
                continue
            if key == "controllers":
                controllers_text = value
                provided_any = True
                continue
            _apply_arg_value(params, key, value)
            provided_any = True
            continue

        if token.startswith("--") and has_next:
            key = _strip_prefix(token, "--")
            value = next_token
            if _is_log_path_key(key):
                log_path = value
                skip_next = True
                continue
            if _is_log_level_key(key):
                log_level = value
                skip_next = True
                continue
            if key == "controllers":
                controllers_text = value
                provided_any = True
                skip_next = True
                continue
            _apply_arg_value(params, key, value)
            provided_any = True
            skip_next = True
            continue

    return params, provided_any, start_without_gui, list_params, controllers_text, suppress_log, log_path, log_level


def _is_suppress_log_key(key: str) -> bool:
    if key is None:
        return False
    lower = key.lower()
    return lower == "supress-log" or lower == "suppress-log" or lower == "supress_log" or lower == "suppress_log"


def _is_log_path_key(key: str) -> bool:
    if key is None:
        return False
    lower = key.lower()
    return lower == "log-path" or lower == "log_path"


def _is_log_level_key(key: str) -> bool:
    if key is None:
        return False
    lower = key.lower()
    return lower == "log-level" or lower == "log_level"


def _is_true_text(value: str) -> bool:
    if value is None:
        return False
    lower = value.strip().lower()
    return lower == "1" or lower == "true" or lower == "yes" or lower == "on"


def _parse_controllers_text(text):
    if text is None:
        return None
    items = text.split(",")
    result = []
    for item in items:
        name = item.strip()
        if name != "":
            result.append(name)
    return result


def _scripts_folder_path():
    base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir, "Scripts")


def _collect_script_names(script_infos):
    return [info.name for info in script_infos]


def _default_controllers(script_names):
    return list(script_names[:10])


def _adjust_controllers_to_players(controllers, players):
    result = list(controllers[:players])
    if len(result) < players:
        result.extend(["mouse"] * (players - len(result)))
    return result

def _controller_options(script_names):
    return ["Mouse"] + list(script_names)


def _filter_visible_scripts(script_infos):
    visible = []
    for info in script_infos:
        if not _is_hidden_script(info.name):
            visible.append(info)
    return visible


def _is_hidden_script(name: str) -> bool:
    if name is None:
        return False
    return name.lower() == "randomauto"

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

def _print_console_help():
    print("Console parameters:")
    print("  --players N or players=N")
    print("  --controllers list (example: --controllers mouse,Adam,Bara)")
    print("")
    print("  --width N or width=N")
    print("  --height N or height=N")
    print("  --track_width_mean N or track_width_mean=N")
    print("  --track_width_var N or track_width_var=N")
    print("  --turn_sharpness N or turn_sharpness=N")
    print("  --turn_density N or turn_density=N")
    print("  --seed N or --seed None")
    print("")
    print("  --supress-log (disable all logging)")
    print("  --log-path PATH or log_path=PATH")
    print("  --log-level LEVEL (DEBUG|INFO|WARNING|ERROR|CRITICAL)")
    print("  --measure or measure=1")
    print("")
    print("  --no-gui (start game directly)")
    print("  --list-params (show this list)")


def _print_start_instructions():
    print("Players: use --players N or players=N")
    print("Measure: use --measure")
    print("Controllers: use --controllers mouse,ScriptName")
    print("Skip GUI: use --no-gui")
    print("List console params: use --list-params")


def main():
    # 1) Gather parameters and available scripts.
    (
        params,
        provided_any,
        start_without_gui,
        list_params,
        controllers_text,
        suppress_log,
        log_path,
        log_level
    ) = _apply_console_args(GameParams())

    if suppress_log:
        setup_logging(log_level, to_console=False, file_path=None)
    else:
        setup_logging(log_level, to_console=True, file_path=log_path)

    if list_params:
        _print_console_help()
        return

    scripts_folder = _scripts_folder_path()
    scripts = load_scripts_from_folder(scripts_folder)
    visible_scripts = _filter_visible_scripts(scripts)
    script_names_all = _collect_script_names(scripts)
    script_names_default = _collect_script_names(visible_scripts)

    # 2) Decide who will control each car (mouse vs script).
    controllers = _parse_controllers_text(controllers_text)
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
        controllers = _default_controllers(script_names_default)
        controllers = _adjust_controllers_to_players(controllers, params.players)
        if not start_without_gui:
            options = _controller_options(script_names_all)
            dialog = ControllerDialog(params.players, options, controllers)
            controllers = dialog.run()
            controllers = _adjust_controllers_to_players(controllers, params.players)
        if start_without_gui:
            params.players = 2
            controllers = []
            controllers.append("mouse")
            controllers.append("mouse")

    # 4) Build the world and assign the chosen drivers.
    # Generate a simple track
    track = generate_track(
        width=params.width,
        height=params.height,
        players=params.players,
        track_width_mean=params.track_width_mean,
        track_width_var=params.track_width_var,
        turn_density=params.turn_density,
        turn_sharpness=params.turn_sharpness,
        seed=params.seed
    )

    # Create cars
    cars = _create_cars_for_track(track, params.players, controllers, scripts)

    # Initialize game state
    game_state = GameState(track=track, cars=cars)
    if params.measure_performance:
        log_path = os.path.join(os.path.dirname(__file__), "performance_log.csv")
        game_state.performance = PerformanceTracker(len(cars), log_path)

    # 5) Hand off to renderer; it drives the game loop until window close.
    # Start the renderer
    renderer = Renderer(game_state)
    _print_start_instructions()
    renderer.run()


if __name__ == "__main__":
    main()
