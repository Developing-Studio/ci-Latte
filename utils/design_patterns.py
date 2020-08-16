from abc import abstractmethod, ABCMeta
from typing import Any, Dict


class SingletonMeta(ABCMeta):
    """
    A `Singleton` Design Pattern by GoF.
    """

    __instances: Dict[object, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances.keys() or cls.__instances[cls] is None:
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]


class Factory():
    """
    A `Factory` Design Pattern by GoF.
    """

    target_cls: Any = None

    @abstractmethod
    def build(self) -> Any:
        """
        Build an item.
        abstractmethod predefined to describe the `Factory` design pattern.
        :return:
        """
        return self.target_cls()