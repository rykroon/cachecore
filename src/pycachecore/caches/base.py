from collections.abc import Iterable
from typing import Any, Optional, Union, Protocol, runtime_checkable
from pycachecore.utils import MissingKey


@runtime_checkable
class CacheInterface(Protocol):

    def get(self, key: str) -> Union[Any, MissingKey]:
        """
            Returns the value associated with the key.
            Returns MissingKey if key is not found.
        """
        ...

    def set(self, key: str, value: Any, ttl: Optional[int]=None):
        """
            Set the value of `value` to key `key`.
            The key will expire after `ttl` seconds.
            The key will never expire if `ttl` is None
        """
        ...

    def add(self, key: str, value: Any, ttl: Optional[int]=None) -> bool:
        ...

    def delete(self, key: str) -> bool:
        """
            Deletes the key
            Returns True if a key was deleted, else False
        """
        ...

    def has_key(self, key: str) -> bool:
        ...

    def get_many(self, keys: list[str]) -> list[Any]:
        ...

    def set_many(self, mapping: Iterable[tuple[str, Any]], ttl: Optional[int]=None):
        ...

    def delete_many(self, keys: list[str]) -> list[bool]:
        """
            Deletes all of the keys in the list.
            Returns a list of boolean values indicating 
                if the key was deleted.
        """
        ...

    def get_ttl(self, key: str) -> Union[int, None, MissingKey]:
        """
            Returns the TTL of the key.
            Return None if key does not have a ttl
            Returns MissingKey if the key does not exist.
        """
        ...

    def set_ttl(self, key: str, ttl: Optional[int]=None):
        """
            Sets the TTL of the key.
        """
        ...

    def incr(self, key, delta=1) -> int:
        ...

    def decr(self, key, delta=1) -> int:
        ...

    def clear(self):
        ...
