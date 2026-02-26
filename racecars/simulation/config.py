"""Console configuration parsing and help text for racecars."""

import argparse
import logging
import os
import sys
from simulation.params import GameParams

_LOGGER = logging.getLogger("racecars.config")


class ConsoleConfig:
    def __init__(
        self,
        params: GameParams,
        provided_any: bool,
        start_without_gui: bool,
        list_params: bool,
        list_advanced_parameters: bool,
        controllers_text,
        suppress_log: bool,
        log_path,
        log_level: str,
    ):
        self.params = params
        self.provided_any = provided_any
        self.start_without_gui = start_without_gui
        self.list_params = list_params
        self.list_advanced_parameters = list_advanced_parameters
        self.controllers_text = controllers_text
        self.suppress_log = suppress_log
        self.log_path = log_path
        self.log_level = log_level


def parse_console_args(default_params: GameParams):
    params = default_params.clone()

    cli_tokens_source = []
    for index in range(1, len(sys.argv)):
        cli_tokens_source.append(sys.argv[index])
    cli_tokens = _normalize_cli_tokens(cli_tokens_source)

    explicit_config_path = _extract_config_path_from_cli(cli_tokens)
    config_path = None
    explicit_config = False
    if explicit_config_path is None:
        config_path = _default_config_path()
    else:
        config_path = explicit_config_path
        explicit_config = True

    config_tokens = _load_config_tokens(config_path, explicit_config)

    all_tokens = []
    for token in config_tokens:
        all_tokens.append(token)
    for token in cli_tokens:
        all_tokens.append(token)

    parser = _build_arg_parser()
    options, unknown_tokens = parser.parse_known_args(all_tokens)
    if len(unknown_tokens) > 0:
        _LOGGER.warning("Ignoring unknown console parameters: %s", str(unknown_tokens))

    _apply_options_to_params(params, options)

    provided_any = _has_parameter_overrides(options)
    start_without_gui = options.start_without_gui
    list_params = options.list_params
    list_advanced_parameters = options.list_advanced_parameters
    controllers_text = options.controllers

    suppress_log = False
    if options.suppress_log is not None:
        suppress_log = options.suppress_log

    log_path = options.log_path
    log_level = "INFO"
    if options.log_level is not None:
        log_level = options.log_level

    return ConsoleConfig(
        params=params,
        provided_any=provided_any,
        start_without_gui=start_without_gui,
        list_params=list_params,
        list_advanced_parameters=list_advanced_parameters,
        controllers_text=controllers_text,
        suppress_log=suppress_log,
        log_path=log_path,
        log_level=log_level,
    )


def parse_controllers_text(text):
    if text is None:
        return None
    items = text.split(",")
    result = []
    for item in items:
        name = item.strip()
        if name != "":
            result.append(name)
    return result


def print_basic_console_help():
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
    print("  --framerate N or framerate=N")
    print("  --seed N or --seed None")
    print("")
    print("  --supress-log or --suppress-log")
    print("  --log-path PATH or log_path=PATH")
    print("  --log-level LEVEL (DEBUG|INFO|WARNING|ERROR|CRITICAL)")
    print("  --measure or measure=1")
    print("")
    print("  --config PATH (default: racecars.config next to main.py)")
    print("  --no-gui or --start (start game directly)")
    print("  --list-params (show this list)")
    print("  --list-advanced-parameters (show advanced rule parameters)")


def print_advanced_console_help():
    print("Advanced console parameters:")
    print("  --car-collision-penalty on|off")
    print("    If OFF, collision with another car does not apply waiting penalty.")
    print("    Default: on")
    print("")
    print("  --shuffle-turn-order on|off")
    print("    If ON, a list of car indexes is shuffled at the start of each round.")
    print("    Car objects are not shuffled.")
    print("    Default: off")
    print("")
    print("  --strict-target-check on|off")
    print("    If ON, PickMove() result must be one of generated target vertices.")
    print("    Default: off")
    print("")
    print("  --penalty-length N")
    print("    Fixed number of waiting rounds after penalty.")
    print("    Default: 2")
    print("")
    print("  --penalty-length vel+N")
    print("    Waiting rounds compensate for deceleration and add the actual penalty.")
    print("    Example: --penalty-length vel+2")


def _build_arg_parser():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument("--players", type=int)
    parser.add_argument("--controllers")
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--track-width-mean", "--track_width_mean", dest="track_width_mean", type=int)
    parser.add_argument("--track-width-var", "--track_width_var", dest="track_width_var", type=int)
    parser.add_argument("--turn-sharpness", "--turn_sharpness", dest="turn_sharpness", type=int)
    parser.add_argument("--turn-density", "--turn_density", dest="turn_density", type=int)
    parser.add_argument("--framerate", type=int)
    parser.add_argument("--seed", type=_parse_seed_option)
    parser.add_argument("--measure", nargs="?", const="on", type=_parse_bool_option)

    parser.add_argument(
        "--suppress-log",
        "--supress-log",
        "--suppress_log",
        "--supress_log",
        dest="suppress_log",
        nargs="?",
        const="on",
        type=_parse_bool_option,
    )
    parser.add_argument("--log-path", "--log_path", dest="log_path")
    parser.add_argument("--log-level", "--log_level", dest="log_level")

    parser.add_argument("--config", dest="config_path")
    parser.add_argument("--no-gui", "--start", dest="start_without_gui", action="store_true")
    parser.add_argument("--list-params", "--help-params", dest="list_params", action="store_true")
    parser.add_argument("--list-advanced-parameters", dest="list_advanced_parameters", action="store_true")

    parser.add_argument(
        "--car-collision-penalty",
        "--car_collision_penalty",
        dest="car_collision_penalty_enabled",
        nargs="?",
        const="on",
        type=_parse_bool_option,
    )
    parser.add_argument(
        "--shuffle-turn-order",
        "--shuffle_turn_order",
        dest="shuffle_turn_order_each_round",
        nargs="?",
        const="on",
        type=_parse_bool_option,
    )
    parser.add_argument(
        "--strict-target-check",
        "--strict_target_check",
        dest="strict_target_check",
        nargs="?",
        const="on",
        type=_parse_bool_option,
    )
    parser.add_argument(
        "--penalty-length",
        "--penalty_length",
        dest="penalty_length",
        type=_parse_penalty_length_option,
    )

    return parser


def _apply_options_to_params(params: GameParams, options):
    if options.width is not None:
        params.width = options.width
    if options.height is not None:
        params.height = options.height
    if options.players is not None:
        params.players = options.players
    if options.track_width_mean is not None:
        params.track_width_mean = options.track_width_mean
    if options.track_width_var is not None:
        params.track_width_var = options.track_width_var
    if options.turn_sharpness is not None:
        params.turn_sharpness = options.turn_sharpness
    if options.turn_density is not None:
        params.turn_density = options.turn_density
    if options.framerate is not None:
        params.framerate = options.framerate
    if options.seed is not None:
        params.seed = options.seed
    if options.measure is not None:
        params.measure_performance = options.measure

    if options.car_collision_penalty_enabled is not None:
        params.car_collision_penalty_enabled = options.car_collision_penalty_enabled
    if options.shuffle_turn_order_each_round is not None:
        params.shuffle_turn_order_each_round = options.shuffle_turn_order_each_round
    if options.strict_target_check is not None:
        params.strict_target_check = options.strict_target_check

    if options.penalty_length is not None:
        penalty_tuple = options.penalty_length
        penalty_mode = penalty_tuple[0]
        penalty_value = penalty_tuple[1]
        params.penalty_mode = penalty_mode
        params.penalty_value = penalty_value


def _has_parameter_overrides(options):
    fields = [
        "players",
        "controllers",
        "width",
        "height",
        "track_width_mean",
        "track_width_var",
        "turn_sharpness",
        "turn_density",
        "framerate",
        "seed",
        "measure",
        "car_collision_penalty_enabled",
        "shuffle_turn_order_each_round",
        "strict_target_check",
        "penalty_length",
    ]
    for name in fields:
        value = getattr(options, name)
        if value is not None:
            return True
    return False


def _default_config_path():
    module_dir = os.path.dirname(__file__)
    racecars_dir = os.path.dirname(module_dir)
    return os.path.join(racecars_dir, "racecars.config")


def _normalize_cli_tokens(tokens):
    result = []
    for token in tokens:
        normalized = token
        if _looks_like_bare_key_value_token(token):
            normalized = "--" + token
        result.append(normalized)
    return result


def _looks_like_bare_key_value_token(token: str):
    if token.startswith("-"):
        return False
    if "=" not in token:
        return False

    parts = token.split("=", 1)
    key = parts[0]
    if key == "":
        return False

    for ch in key:
        if ch.isalnum():
            continue
        if ch == "_" or ch == "-":
            continue
        return False
    return True


def _extract_config_path_from_cli(cli_tokens):
    path_value = None

    index = 0
    while index < len(cli_tokens):
        token = cli_tokens[index]
        if token.startswith("--config="):
            eq_index = token.find("=")
            if eq_index >= 0 and eq_index + 1 < len(token):
                path_value = ""
                index2 = eq_index + 1
                while index2 < len(token):
                    path_value = path_value + token[index2]
                    index2 += 1
            else:
                path_value = ""
            index += 1
            continue

        if token == "--config":
            if index + 1 < len(cli_tokens):
                path_value = cli_tokens[index + 1]
                index += 2
                continue
            path_value = ""
            index += 1
            continue

        index += 1

    return path_value


def _load_config_tokens(config_path: str, required: bool):
    if config_path is None:
        return []

    if not os.path.isfile(config_path):
        if required:
            try:
                raise FileNotFoundError(config_path)
            except FileNotFoundError as ex:
                _LOGGER.exception("Config file was explicitly requested but not found: %s", str(ex))
        return []

    file_obj = None
    lines = []
    try:
        file_obj = open(config_path, "r", encoding="utf-8")
        lines = file_obj.readlines()
    finally:
        if file_obj is not None:
            file_obj.close()

    tokens = []
    for line in lines:
        new_tokens = _config_line_to_tokens(line)
        for token in new_tokens:
            tokens.append(token)
    return tokens


def _config_line_to_tokens(line: str):
    text = line.strip()
    tokens = []

    if text == "":
        return tokens
    if text.startswith("#") or text.startswith(";"):
        return tokens

    if "=" in text:
        parts = text.split("=", 1)
        key = parts[0].strip()
        value = parts[1].strip()
        if key == "":
            return tokens
        key_token = _ensure_option_prefix(key)
        tokens.append(key_token + "=" + value)
        return tokens

    tokens.append(_ensure_option_prefix(text))
    return tokens


def _ensure_option_prefix(text: str):
    if text.startswith("--"):
        return text
    if text.startswith("-"):
        result = "-"
        for index in range(1, len(text)):
            result = result + text[index]
        return result
    return "--" + text


def _parse_bool_option(text: str):
    if text is None:
        raise argparse.ArgumentTypeError("Boolean value is required.")
    lower = text.strip().lower()
    if lower == "1" or lower == "true" or lower == "yes" or lower == "on":
        return True
    if lower == "0" or lower == "false" or lower == "no" or lower == "off":
        return False
    raise argparse.ArgumentTypeError("Use on/off, true/false, yes/no, or 1/0.")


def _parse_seed_option(text: str):
    if text is None:
        return None
    value = text.strip()
    lower = value.lower()
    if lower == "" or lower == "none":
        return None
    if _is_int_string(value, True):
        return int(value)
    raise argparse.ArgumentTypeError("Seed must be integer or None.")


def _parse_penalty_length_option(text: str):
    if text is None:
        raise argparse.ArgumentTypeError("Penalty length value is required.")

    value = text.strip().lower()
    if _is_int_string(value, False):
        return ("fixed", int(value))

    prefix = "vel+"
    if value.startswith(prefix):
        suffix = ""
        for index in range(len(prefix), len(value)):
            suffix = suffix + value[index]
        if _is_int_string(suffix, False):
            return ("velocity_plus", int(suffix))

    raise argparse.ArgumentTypeError("Use N or vel+N (example: 2 or vel+1).")


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
