"""
utils.tools

"""
from argparse import ArgumentTypeError
from typing import Dict, Any, Tuple, Union, List, NoReturn


def cast_to_bool(arg: str):
    # True case
    if arg in ["True", "true", "1"]:
        return True

    # False case
    elif arg in ["False", "false", "0"]:
        return False

    # Not suitable args
    else:
        msg = f"Cannot cast an argument `{arg}` into boolean : Not a boolean indicator"
        raise ArgumentTypeError(msg)


class NotNull(Exception):
    def __init__(self, key: str, kwargs: Dict[str, Any]):
        self.key = key
        self.kwargs = kwargs

    def __str__(self) -> str:
        return f"key {self.key} in kwargs {self.kwargs} can not be null value (none)"

    def __repr__(self):
        return self.__str__()


def get_value_from_kwargs(key: str, kwargs: Dict[str, Any], notnull: bool = False) -> Union[Dict[str, Any], NoReturn]:
    if key in kwargs.keys():
        return kwargs.pop(key)
    else:
        if notnull:
            raise NotNull(key=key, kwargs=kwargs)
        else:
            return None


def parse_args_from_kwargs(key: Union[str, Tuple[str, ...]], kwargs: Dict[str, Any], default: Any = None) -> Any:
    
    if type(key) == str:
        return kwargs.pop(key) if key in kwargs else default
    elif type(key) == tuple:
        results: List[Any] = []
        for key_choice in key:
            if key_choice in kwargs:
                results.append(kwargs.pop(key_choice))

        if len(results) > 1:
            raise KeyError("[utils.parse_args_from_kwargs] Cannot parse two or more keys at once!"
                           "Use this function for each single keys.")
        else:
            return results[0]


def get_cog_name_in_ext(ext_map: Dict[str, Dict[str, str]], module_path: str) -> str:
    return [key for key, value in ext_map.get(module_path.split('.')[1]).items() if value == module_path][0]