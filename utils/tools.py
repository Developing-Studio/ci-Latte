"""
utils.tools

"""
from argparse import ArgumentTypeError
from typing import Dict


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


def get_cog_name_in_ext(ext_map: Dict[str, Dict[str, str]], module_path: str) -> str:
    return [key for key, value in ext_map.get(module_path.split('.')[1]).items() if value == module_path][0]