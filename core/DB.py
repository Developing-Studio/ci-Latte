from typing import Tuple, Any, Dict, Union
from abc import abstractmethod
import discord, sqlalchemy

Key = Union[str, int, bytes]


class DatabaseWrapper:
    SQL_QUERY = Tuple[str, Tuple[Any]]
    __create_sql__: str = ""

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

    @abstractmethod
    def connect(self):
        """
        connect to DB
        """

    @abstractmethod
    def close(self):
        """
        close the DB connection
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the DB is connected
        :return: boolean value which indicates wheter DB is connected or not.
        """
        pass

    @abstractmethod
    def custom_query(self, query: str, params: Tuple[Any]) -> Any:
        """
        Post a custom query and retrieve response.
        :param query: a query to process
        :param params: a parameter used in query
        :return:
        """
        pass

    @abstractmethod
    def create(self):
        """
        Create inital tables to use.
        self.__create_sql__ is used to create DB contents.
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
        pass

    def set(self, user_id: int, **datas: Dict[Key, Any]):
        """
        Set user data
        :param user_id:
        :param datas:
        :return:
        """
        pass


class GuildDB(DatabaseWrapper):
    def get(self, guild_id: int, **options: Dict[Key, Any]) -> Any:
        """
        Get guild data
        :param user_id:
        :param options:
        :return:
        """
        pass

    def set(self, user_id: int, **datas: Dict[Key, Any]):
        """
        Set guild data
        :param user_id:
        :param datas:
        :return:
        """
        pass
