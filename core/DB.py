from typing import Tuple, Any, Dict, Union
import sqlite3
import discord

Key = Union[str, int, bytes]


class DatabaseWrapper:
    SQL_QUERY = Tuple[str, Tuple[Any]]

    db_connection: sqlite3.Connection = None

    def __init__(self, db_dir: str):
        self.db_dir = db_dir

    @classmethod
    def defend_sql_injection(self, query: str, params: Tuple[Any]) -> SQL_QUERY:
        """
        Validate given_query to defend sql_injections
        :param query: query to validate.
        :param params: paramse needed in query
        :return: validated and fixed query
        """
        pass

    def connect(self):
        self.db_connection = sqlite3.connect(database=self.db_dir)

    def close(self):
        self.db_connection.close()

    def post(self, query: str, params: Tuple[Any]) -> Any:
        """
        Post a custom query and retrieve response.
        :param query:
        :param params:
        :return:
        """
        pass


class UserDB(DatabaseWrapper):
    def get(self, user_id: int, **options: Dict[Key, Any]) -> Any:
        """
        Get user data
        :param user_id:
        :param options:
        :return:
        """

    def set(self, user_id: int, **datas: Dict[Key, Any]):
        """
        Set user data
        :param user_id:
        :param datas:
        :return:
        """


class GuildDB(DatabaseWrapper):
    def get(self, guild_id: int, **options: Dict[Key, Any]) -> Any:
        """
        Get guild data
        :param user_id:
        :param options:
        :return:
        """

    def set(self, user_id: int, **datas: Dict[Key, Any]):
        """
        Set guild data
        :param user_id:
        :param datas:
        :return:
        """
