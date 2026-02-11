import os
import sys
from simulation.game_state import GameState, create_cars_for_track
from simulation.track_generator import generate_track
from simulation.params import GameParams
from simulation.manual_auto import MouseAuto
from simulation.script_loader import load_scripts_from_folder
from simulation.performance import PerformanceTracker
from ui.renderer import Renderer
from ui.setup_dialog import SetupDialog
from ui.controller_dialog import ControllerDialog


def _is_int_string(text: str, allow_negative: bool):
    if text == "":
        return False
    index = 0
    if allow_negative and text[0] == "-":
        if len(text) == 1:
            return False
        index = 1
    while index < len(text):
        if not text[index].isdigit():
            return False
        index += 1
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
    result = ""
    index = len(prefix)
    while index < len(text):
        result = result + text[index]
        index += 1
    return result


def _apply_arg_value(params: GameParams, key: str, value: str):
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
    params = default_params.clone()
    args = []
    index = 1
    while index < len(sys.argv):
        args.append(sys.argv[index])
        index += 1

    index = 0
    provided_any = False
    start_without_gui = False
    list_params = False
    controllers_text = None
    while index < len(args):
        token = args[index]
        if token == "--no-gui" or token == "--start":
            start_without_gui = True
            index += 1
            continue
        if token == "--measure":
            params.measure_performance = True
            provided_any = True
            index += 1
            continue
        if token == "--list-params" or token == "--help-params":
            list_params = True
            index += 1
            continue
        key, value = _parse_arg_pair(token)
        if key is not None:
            if key == "controllers":
                controllers_text = value
                provided_any = True
                index += 1
                continue
            _apply_arg_value(params, key, value)
            provided_any = True
            index += 1
            continue

        if token.startswith("--") and index + 1 < len(args):
            key = _strip_prefix(token, "--")
            value = args[index + 1]
            if key == "controllers":
                controllers_text = value
                provided_any = True
                index += 2
                continue
            _apply_arg_value(params, key, value)
            provided_any = True
            index += 2
            continue

        index += 1

    return params, provided_any, start_without_gui, list_params, controllers_text


def _parse_controllers_text(text):
    if text is None:
        return None
    items = text.split(",")
    result = []
    index = 0
    while index < len(items):
        name = items[index].strip()
        if name != "":
            result.append(name)
        index += 1
    return result


def _scripts_folder_path():
    base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir, "Scripts")


def _collect_script_names(script_infos):
    names = []
    index = 0
    while index < len(script_infos):
        names.append(script_infos[index].name)
        index += 1
    return names


def _default_controllers(script_names):
    controllers = []
    index = 0
    while index < len(script_names) and index < 10:
        controllers.append(script_names[index])
        index += 1
    return controllers


def _adjust_controllers_to_players(controllers, players):
    result = _copy_list(controllers)
    while len(result) > players:
        result.pop()
    while len(result) < players:
        result.append("mouse")
    return result


def _copy_list(items):
    result = []
    index = 0
    while index < len(items):
        result.append(items[index])
        index += 1
    return result


def _controller_options(script_names):
    options = []
    options.append("Mouse")
    index = 0
    while index < len(script_names):
        options.append(script_names[index])
        index += 1
    return options


def _filter_visible_scripts(script_infos):
    visible = []
    index = 0
    while index < len(script_infos):
        info = script_infos[index]
        if not _is_hidden_script(info.name):
            visible.append(info)
        index += 1
    return visible


def _is_hidden_script(name: str) -> bool:
    if name is None:
        return False
    return name.lower() == "randomauto"


def _is_mouse_name(name: str) -> bool:
    if name is None:
        return False
    return name.lower() == "mouse"


def _find_script_info(script_infos, name: str):
    if name is None:
        return None
    target = name.lower()
    index = 0
    while index < len(script_infos):
        info = script_infos[index]
        if info.name.lower() == target:
            return info
        index += 1
    return None


def _assign_drivers(cars, controllers, script_infos):
    index = 0
    while index < len(cars):
        car = cars[index]
        controller_name = "mouse"
        if index < len(controllers):
            controller_name = controllers[index]

        if _is_mouse_name(controller_name):
            car.SetDriver(MouseAuto())
        else:
            info = _find_script_info(script_infos, controller_name)
            if info is None:
                car.SetDriver(MouseAuto())
            else:
                driver = info.auto_class()
                car.SetDriver(driver)
                name = ""
                if hasattr(driver, "GetName"):
                    name = driver.GetName()
                if name == "":
                    name = info.name
                car.name = name

        index += 1


def _print_console_help():
    print("Console parameters:")
    print("  --width N or width=N")
    print("  --height N or height=N")
    print("  --players N or players=N")
    print("  --track_width_mean N or track_width_mean=N")
    print("  --track_width_var N or track_width_var=N")
    print("  --turn_sharpness N or turn_sharpness=N")
    print("  --turn_density N or turn_density=N")
    print("  --seed N or --seed None")
    print("  --measure or measure=1")
    print("  --controllers list (example: --controllers mouse,Adam,Bara)")
    print("  --no-gui (start game directly)")
    print("  --list-params (show this list)")


def _print_start_instructions():
    print("Players: use --players N or players=N")
    print("Measure: use --measure")
    print("Controllers: use --controllers mouse,ScriptName")
    print("Skip GUI: use --no-gui")
    print("List console params: use --list-params")


def main():
    params, provided_any, start_without_gui, list_params, controllers_text = _apply_console_args(GameParams())
    if list_params:
        _print_console_help()
        return

    scripts_folder = _scripts_folder_path()
    scripts = load_scripts_from_folder(scripts_folder)
    visible_scripts = _filter_visible_scripts(scripts)
    script_names_all = _collect_script_names(scripts)
    script_names_default = _collect_script_names(visible_scripts)

    controllers = _parse_controllers_text(controllers_text)
    if controllers is not None and len(controllers) == 0:
        controllers = None

    if controllers is None and not provided_any and not start_without_gui and len(script_names_default) > 0:
        params.players = len(script_names_default)
        if params.players > 10:
            params.players = 10

    if controllers is not None:
        params.players = len(controllers)

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

    # Generate a simple track
    track = generate_track(
        width=params.width - 2,
        height=params.height - 2,
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
    track.finish_line.start.x = params.width - 1
    track.finish_line.end.x = params.width - 1

    # Create cars
    cars = create_cars_for_track(track, params.players)
    # move cars to start properly
    for car in cars:
        car.pos.x = 1
    _assign_drivers(cars, controllers, scripts)

    # Initialize game state
    game_state = GameState(track=track, cars=cars)
    if params.measure_performance:
        log_path = os.path.join(os.path.dirname(__file__), "performance_log.csv")
        game_state.performance = PerformanceTracker(len(cars), log_path)

    # Start the renderer
    renderer = Renderer(game_state)
    _print_start_instructions()
    renderer.run()


if __name__ == "__main__":
    main()
