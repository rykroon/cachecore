from abc import abstractmethod
from typing import Any, Iterable
from .utils import KEEP_TTL


class CacheInterface:

    @abstractmethod
    def get(self, key: str, default=None):
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ex: int | None = None):
        """Assign a value to a key.

        :param key: The key to be set.
        :param value: The value to be stored.
        :param ex: The time-to-live. If None, then the value will not expire.
        """
        pass

    @abstractmethod
    def add(self, key: str, value: Any, ex: int | None = None) -> bool:
        """Set the value only if the key doesn't already exist.

        :param key: The key to be set.
        :param value: The value to be stored.
        :param ttl: The time-to-live.
        :returns: True, if the key was added, else False.
        """
        pass

    @abstractmethod
    def replace(self, key: str, value: Any) -> bool:
        pass

    @abstractmethod
    def delete(self, *keys: str) -> int:
        pass

    @abstractmethod
    def exists(self, *keys: str) -> int:
        pass

    def __contains__(self, key: str) -> bool:
        return self.exists(key) == 1
    
    @abstractmethod
    def ttl(self, key: str) -> int:
        pass

    @abstractmethod
    def incr(self, key, amount: int = 1) -> int:
        """Increment the value associated with the key.
        Creates the key if it does not exist.

        :param key: The key.
        :param delta: The amount to increment.
        :returns: The amount.
        """
        pass

    @abstractmethod
    def decr(self, key, amount: int = 1) -> int:
        """Decrement the value associated with the key.
        Creates the key if it does not exist.

        :param key: The key.
        :param delta: The amount to decrement.
        :returns: The amount.
        """
        pass

    @abstractmethod
    def clear(self):
        pass
