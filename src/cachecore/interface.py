from abc import abstractmethod
from typing import Any, Iterable
from .utils import KEEP_TTL


class CacheInterface:

    @abstractmethod
    def get(self, key: str, default=None):
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int | None = None):
        """Assign a value to a key.

        :param key: The key to be set.
        :param value: The value to be stored.
        :param ttl: The time-to-live. If None, then the value will not expire.
        """
        pass

    @abstractmethod
    def add(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set the value only if the key doesn't already exist.

        :param key: The key to be set.
        :param value: The value to be stored.
        :param ttl: The time-to-live.
        :returns: True, if the key was added, else False.
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    def has(self, key: str) -> bool:
        pass

    @abstractmethod
    def get_or_set(self, key: str, value: Any, ttl: int | None = None):
        pass

    @abstractmethod
    def get_many(self, keys: Iterable[str], default: Any = None) -> Iterable[Any]:
        """Returns an iterable of values.

        :param keys: An iterable of keys to retrieve.
        :param default: A default value in case a key is not found.
        :returns: An iterable of values.
        """
        pass

    @abstractmethod
    def set_many(self, mapping: Iterable[tuple[str, Any]], ttl: int | None = None):
        """Stores the mapping of key value pairs.

        :param mapping: An iterable of key, value tuples.
        :param ttl: The time-to-live.
        """
        pass

    @abstractmethod
    def delete_many(self, keys: Iterable[str]) -> Iterable[bool]:
        """Deletes all of the keys in the iterable.

        :param keys: An iterable of keys to be deleted.
        :returns: An iterable of boolean values indicating if the key was deleted.
        """
        pass

    @abstractmethod
    def touch(self, key: str, ttl: int | None = None) -> bool:
        """Sets the TTL of the key.

        :param key: The key.
        :param ttl: The time-to-live.
        :returns: True, if the TTL was updated, else False.
        """
        pass

    @abstractmethod
    def incr(self, key, delta=1) -> int:
        """Increment the value associated with the key.
        Creates the key if it does not exist.

        :param key: The key.
        :param delta: The amount to increment.
        :returns: The amount.
        """
        pass

    @abstractmethod
    def decr(self, key, delta=1) -> int:
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
