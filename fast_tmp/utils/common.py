import importlib
from typing import Any


def import_module(module_path: str) -> Any:
    path_list = module_path.split(".")
    mod = importlib.import_module(".".join(path_list[0:-1]))
    for k, v in mod.__dict__.items():
        if k == path_list[-1]:
            return v
