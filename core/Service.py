"""
core/Service.py
~~~~~~~~~~~~~~~
Module for codes used in entire Latte`s service.

User : Latte`s signed discord user dataclass. Used to store basic informations, extension informations, and user-by-user systems like alarms, etc.
Guild : Latte`s signed discord guild dataclass. Used to store basic informations, extension informations, guild-local configs, and guild-local events, etc.
"""
import datetime
from dataclasses import dataclass
from typing import Union


@dataclass
class LatteUser:
    # Basic Info
    snowflakes_id: int
    name: str
    assigned_when: Union[str, datetime.datetime]


@dataclass
class LatteGuild:
    # Basic Info
    snowflakes_id: int
    name: str
    assigned_when: Union[str, datetime.datetime]