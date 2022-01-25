from collections.abc import Iterable
from typing import Any, Optional, Union, Protocol, runtime_checkable
from cachecore.utils import MissingKey


@runtime_checkable
class BackendProtocol(Protocol):

    def get(self, key: str) -> Union[Any, MissingKey]:
        """
            Returns the value associated with the key.
            Returns MissingKey if key is not found.
        """
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl: Optional[int]=None):
        """
            Set the value of `value` to key `key`.
            The key will expire after `ttl` seconds.
            The key will never expire if `ttl` is None
        """
        raise NotImplementedError

    def add(self, key: str, value: Any, ttl: Optional[int]=None) -> bool:
        raise NotImplementedError

    def delete(self, key: str) -> bool:
        """
            Deletes the key
            Returns True if a key was deleted, else False
        """
        raise NotImplementedError

    def has_key(self, key: str) -> bool:
        raise NotImplementedError

    def get_many(self, keys: list[str]) -> list[Any]:
        raise NotImplementedError

    def set_many(self, mapping: Iterable[tuple[str, Any]], ttl: Optional[int]=None):
        raise NotImplementedError

    def delete_many(self, keys: list[str]) -> list[bool]:
        """
            Deletes all of the keys in the list.
            Returns a list of boolean values indicating 
                if the key was deleted.
        """
        raise NotImplementedError

    def get_ttl(self, key: str) -> Union[int, None, MissingKey]:
        """
            Returns the TTL of the key.
            Return None if key does not have a ttl
            Returns MissingKey if the key does not exist.
        """
        raise NotImplementedError

    def set_ttl(self, key: str, ttl: Optional[int]=None):
        """
            Sets the TTL of the key.
        """
        raise NotImplementedError

    def incrby(self, key, delta):
        raise NotImplementedError

    def decrby(self, key, delta):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError
