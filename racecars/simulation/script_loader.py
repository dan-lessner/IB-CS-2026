"""Load student driver scripts from the Scripts folder at runtime."""

import logging
import os
import sys
import importlib.util

_LOGGER = logging.getLogger("racecars.script_loader")


class ScriptInfo:
    def __init__(self, name: str, path: str, file_name: str):
        # Metadata plus a cached Auto class once imported.
        self.name = name
        self.path = path
        self.file_name = file_name
        self.auto_class = None


def load_scripts_from_folder(folder_path: str):
    # Discover candidate files first, then convert each into ScriptInfo objects.
    files = _find_script_files(folder_path)
    scripts = []

    for path in files:
        file_name = os.path.basename(path)
        script_name = _filename_without_extension(file_name)
        scripts.append(ScriptInfo(script_name, path, file_name))

    return scripts


def load_auto_class(script_info: ScriptInfo):
    # Lazy import: only import a script when it is actually selected as a controller.
    if script_info is None:
        _LOGGER.warning("load_auto_class() was called with script_info=None.")
        return None
    if script_info.auto_class is not None:
        return script_info.auto_class

    _ensure_repo_root_on_sys_path()
    module_name = _module_name_from_path(script_info.path)
    try:
        module = _load_module(script_info.path, module_name)
    except Exception as ex:
        _LOGGER.exception(
            "Failed to import script '%s' from '%s' (%s: %s).",
            script_info.name,
            script_info.path,
            type(ex).__name__,
            ex
        )
        return None
    if module is None:
        _LOGGER.warning("Script module could not be loaded for '%s'.", script_info.path)
        return None
    if not hasattr(module, "Auto"):
        _LOGGER.warning("Script '%s' does not define required class Auto.", script_info.path)
        return None

    auto_class = getattr(module, "Auto")
    script_info.auto_class = auto_class
    return auto_class


def _find_script_files(folder_path: str):
    # Keep list deterministic to make the UI order stable.
    if not os.path.isdir(folder_path):
        _LOGGER.warning("Scripts folder not found: %s", folder_path)
        return []

    files = []
    names = os.listdir(folder_path)
    for name in names:
        if _is_python_file(name) and not name.startswith("_"):
            full_path = os.path.join(folder_path, name)
            files.append(full_path)

    files.sort()
    return files


def _is_python_file(name: str) -> bool:
    lower = name.lower()
    return lower.endswith(".py")


def _load_module(path: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        _LOGGER.warning("Import spec creation failed for script '%s'.", path)
        return None
    loader = spec.loader
    if loader is None:
        _LOGGER.warning("Import loader creation failed for script '%s'.", path)
        return None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def _module_name_from_path(path: str) -> str:
    base = os.path.basename(path)
    name = _filename_without_extension(base)
    # Using full normalized path keeps module name stable and unique per file.
    normalized = os.path.abspath(path).lower()
    suffix = "".join(ch if ch.isalnum() else "_" for ch in normalized)
    return "script_" + name + "_" + suffix


def _filename_without_extension(name: str) -> str:
    dot_index = name.rfind(".")

    if dot_index <= 0:
        return name

    return name[:dot_index]


def _ensure_repo_root_on_sys_path():
    this_dir = os.path.dirname(__file__)
    repo_root = os.path.abspath(os.path.join(this_dir, ".."))
    if repo_root in sys.path:
        return
    sys.path.insert(0, repo_root)
