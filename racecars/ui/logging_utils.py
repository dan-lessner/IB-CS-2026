"""Shared logging configuration and logger helpers for racecars."""

import logging
import os

_DEFAULT_LOG_LEVEL = "INFO"
_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
_DATE_FORMAT = "%H:%M:%S"


def setup_logging(level, to_console: bool = True, file_path: str = None):
    """Configure root logging handlers and return the resolved level name."""
    root = logging.getLogger()
    _remove_handlers(root)
    logging.disable(logging.NOTSET)
    root.setLevel(logging.NOTSET)

    level_name, level_value, is_valid = _resolve_level(level)
    formatter = logging.Formatter(_FORMAT, datefmt=_DATE_FORMAT)
    has_handler = False

    if to_console:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level_value)
        stream_handler.setFormatter(formatter)
        root.addHandler(stream_handler)
        has_handler = True

    resolved_file_path = None
    if file_path is not None and file_path.strip() != "":
        try:
            resolved_file_path = os.path.abspath(file_path)
            _ensure_parent_dir_exists(resolved_file_path)
            file_handler = logging.FileHandler(resolved_file_path, encoding="utf-8")
            file_handler.setLevel(level_value)
            file_handler.setFormatter(formatter)
            root.addHandler(file_handler)
            has_handler = True
        except Exception as ex:
            logging.getLogger("racecars.logging").warning(
                "Failed to configure file logging for path '%s' (%s): %s",
                file_path,
                type(ex).__name__,
                ex
            )

    if not has_handler:
        logging.disable(logging.CRITICAL)

    logger = logging.getLogger("racecars.logging")
    if has_handler and not is_valid:
        logger.warning("Unknown log level '%s'. Falling back to %s.", level, _DEFAULT_LOG_LEVEL)
    if has_handler:
        logger.debug(
            "Logging enabled (level=%s, console=%s, file=%s).",
            level_name,
            to_console,
            resolved_file_path,
        )
    return level_name

def _resolve_level(level):
    text = _DEFAULT_LOG_LEVEL
    if level is not None:
        text = str(level).strip().upper()
    if text == "DEBUG":
        return text, logging.DEBUG, True
    if text == "INFO":
        return text, logging.INFO, True
    if text == "WARNING":
        return text, logging.WARNING, True
    if text == "ERROR":
        return text, logging.ERROR, True
    if text == "CRITICAL":
        return text, logging.CRITICAL, True
    return _DEFAULT_LOG_LEVEL, logging.INFO, False


def _ensure_parent_dir_exists(file_path: str):
    parent = os.path.dirname(file_path)
    if parent == "":
        return
    os.makedirs(parent, exist_ok=True)


def _remove_handlers(logger):
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        try:
            handler.close()
        except Exception as ex:
            logging.getLogger("racecars.logging").warning(
                "Failed to close previous log handler (%s): %s",
                type(ex).__name__,
                ex
            )

def sanitize_logger_name(text: str):
    if text is None:
        return "unnamed"
    stripped = text.strip()
    if stripped == "":
        return "unnamed"

    result = "".join(ch.lower() if ch.isalnum() else "_" for ch in stripped)

    result = "_".join(part for part in result.split("_") if part != "")
    if result == "":
        return "unnamed"
    return result
