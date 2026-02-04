import os
import sys
import importlib.util


class ScriptInfo:
    def __init__(self, name: str, path: str, auto_class):
        self.name = name
        self.path = path
        self.auto_class = auto_class


def load_scripts_from_folder(folder_path: str):
    _ensure_repo_root_on_sys_path()
    files = _find_script_files(folder_path)
    scripts = []

    index = 0
    while index < len(files):
        path = files[index]
        module_name = _module_name_from_path(path, index)
        module = _load_module(path, module_name)
        if module is not None and hasattr(module, "Auto"):
            auto_class = getattr(module, "Auto")
            file_name = os.path.basename(path)
            script_name = _filename_without_extension(file_name)
            scripts.append(ScriptInfo(script_name, path, auto_class))
        index += 1

    return scripts


def _find_script_files(folder_path: str):
    if not os.path.isdir(folder_path):
        return []

    files = []
    names = os.listdir(folder_path)
    index = 0
    while index < len(names):
        name = names[index]
        if _is_python_file(name) and not name.startswith("_"):
            full_path = os.path.join(folder_path, name)
            files.append(full_path)
        index += 1

    files.sort()
    return files


def _is_python_file(name: str) -> bool:
    lower = name.lower()
    return lower.endswith(".py")


def _load_module(path: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        return None
    loader = spec.loader
    if loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def _module_name_from_path(path: str, index: int) -> str:
    base = os.path.basename(path)
    name = _filename_without_extension(base)
    return "script_" + name + "_" + str(index)


def _filename_without_extension(name: str) -> str:
    dot_index = -1
    index = 0
    while index < len(name):
        if name[index] == ".":
            dot_index = index
        index += 1

    if dot_index <= 0:
        return name

    result = ""
    index = 0
    while index < dot_index:
        result = result + name[index]
        index += 1
    return result


def _ensure_repo_root_on_sys_path():
    this_dir = os.path.dirname(__file__)
    repo_root = os.path.abspath(os.path.join(this_dir, ".."))
    index = 0
    while index < len(sys.path):
        if sys.path[index] == repo_root:
            return
        index += 1
    sys.path.insert(0, repo_root)
