from datetime import datetime
from typing import Tuple, Any, Dict, Union
import sqlalchemy
from sqlalchemy import Column, INTEGER, String, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from utils import get_value_from_kwargs


def defend_sql_injection(query: str, params: Tuple[Any, ...]) -> Tuple[str, Tuple[Any, ...]]:
    """
    Validate given_query to defend sql_injections
    :param query: query to validate.
    :param params: paramse needed in query
    :return: validated and fixed query
    """
    pass


# Define and create the table
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    # Basic Information
    id = Column(INTEGER, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    level = Column(INTEGER, nullable=False)

    # Economy
    wallet = Column(INTEGER)

    def __init__(self, name, level=0, wallet=0):
        self.name = name
        self.level = level

    def __repr__(self):
        return f"<User({self.name}, {self.level})>"


"""
Guild side tables
"""


class Guild(Base):
    __tablename__ = "guilds"

    # Basic Information
    id = Column(INTEGER, primary_key=True)
    name = Column(String, nullable=False)

    # Guild-specific latte configuration
    prefix = Column(String, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Guild({self.id}{self.name})>"


class WarnRecord(Base):
    __tablename__ = "warns"

    # Basic Information
    id = Column(INTEGER, primary_key=True, nullable=False, autoincrement=True)

    # Guild Information
    guild_id = Column(INTEGER, nullable=False)
    guild_name = Column(String)

    # User Information
    user_id = Column(INTEGER, nullable=False)
    user_name = Column(String)

    # Warn information
    reason = Column(String)
    when = Column(DATETIME, nullable=False)

    def __init__(self, guild_id: int, guild_name: str, user_id: int, user_name: str, when: datetime, reason: str):
        # Guild Information
        self.guild_id = guild_id
        self.guild_name = guild_name

        # User Information
        self.user_id = user_id
        self.user_name = user_name

        # Warn information
        self.when = when
        self.reason = reason

    def __repr__(self):
        return f"<WarnRecord({self.id}, {self.guild_id}, {self.user_id}, {self.when}, {self.reason})>"


class MuteRecord(Base):
    __tablename__ = "mutes"

    # Basic Information
    id = Column(INTEGER, primary_key=True, nullable=False, autoincrement=True)

    # Guild Information
    guild_id = Column(INTEGER, nullable=False)
    guild_name = Column(String)

    # User Information
    user_id = Column(INTEGER, nullable=False)
    user_name = Column(String)

    # Mute information
    reason = Column(String, default="UNDEFINED")
    start = Column(DATETIME, nullable=False)
    end = Column(DATETIME, nullable=False)

    def __init__(self, guild_id: int, guild_name: str, user_id: int, user_name: str, start: datetime, end: datetime, reason: str):
        # Guild Information
        self.guild_id = guild_id
        self.guild_name = guild_name

        # User Information
        self.user_id = user_id
        self.user_name = user_name

        # Mute information
        self.start = start
        self.end = end
        self.reason = reason

    def __repr__(self):
        return f"<MuteRecord({self.id},{self.guild_id},{self.user_id},{self.start}~{self.end},{self.reason})>"


class DBWrapper:
    users_engine = None
    guilds_engine = None

    def __init__(self, **attrs):
        self.id = get_value_from_kwargs("id", attrs, notnull=True)
        self.pw = get_value_from_kwargs("pw", attrs, notnull=True)
        self.host = get_value_from_kwargs("host", attrs, notnull=True)
        self.port = get_value_from_kwargs("port", attrs, notnull=True)

    def create_engine(self):
        # Define the MySQL engine using MySQL Connector/Python
        base_uri = f"mysql+mysqlconnector://{self.id}:{self.pw}@{self.host}:{self.port}"

        # guilds database(schema)
        self.guilds_engine = sqlalchemy.create_engine(
            f"{base_uri}/latte_guild",
            echo=True,
            convert_unicode=False
        )

        # users database(schema)
        self.users_engine = sqlalchemy.create_engine(
            f"{base_uri}/latte_user",
            echo=True,
            convert_unicode=False
        )
