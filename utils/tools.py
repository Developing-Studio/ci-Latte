"""
utils.tools

"""
from argparse import ArgumentTypeError


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