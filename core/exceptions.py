from typing import Optional

from discord import DiscordException


class LatteException(DiscordException):
    """
    Exception to describe error on Latte`s features.
    """
    def __init__(self, msg: str):
        self.msg = msg


class ExtException(LatteException):
    """
    Exception to describe error on Latte`s extension feature.
    """
    pass


class BadExtArguments(ExtException):
    """
    Exception to describe bad arguments passed on extension - load/unload/reload features
    """
    def __init__(self, msg: str, ext_category: Optional[str] = None, ext_name: Optional[str] = None, ext_dir: Optional[str] = None):
        self.ext_category = ext_category
        self.ext_name = ext_name
        self.ext_dir = ext_dir
        super(BadExtArguments, self).__init__(msg)

    def __str__(self) -> str:
        return self.msg + f"\nArguments passed : -c {self.ext_category} -n {self.ext_name} -d {self.ext_dir}"