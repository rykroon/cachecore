from collections.abc import Iterable
from typing import Any, Optional, Protocol, runtime_checkable


@runtime_checkable
class CacheInterface(Protocol):

    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str, value: Any):
        ...

    def __delitem__(self, key: str):
        ...

    def __contains__(self, key: str):
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """
            Returns the value assigned to the key.
            Returns default if key is not found.
        """
        ...

    def set(self, key: str, value: Any, ttl: Optional[int]=None):
        """
            Assign a value to a key.
            The key will expire after `ttl` seconds.
            The key will never expire if `ttl` is None.
        """
        ...

    def add(self, key: str, value: Any, ttl: Optional[int]=None) -> bool:
        ...

    def delete(self, key: str) -> bool:
        """
            Deletes the key.
            Returns True if a key was deleted, else False.
        """
        ...

    def has_key(self, key: str) -> bool:
        ...

    def get_many(self, keys: list[str], default: Any = None) -> list[Any]:
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

    def get_ttl(self, key: str, default: Any = 0) -> Optional[int]:
        """
            Returns the TTL of the key.
            Returns None if key does not have a ttl.
            Returns default if the key does not exist.
        """
        ...

    def set_ttl(self, key: str, ttl: Optional[int]=None) -> bool:
        """
            Sets the TTL of the key.
            Returns True or False if the TTL was set.
        """
        ...

    def incr(self, key, delta=1) -> int:
        ...

    def decr(self, key, delta=1) -> int:
        ...

    def clear(self):
        ...


class BaseCache:

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def add(self, key, value, ttl=None):
        if self.has_key(key):
            return False
        self.set(key, value, ttl)
        return True

    def delete(self, key):
        try:
            del self[key]
        except KeyError:
            return False
        return True

    def has_key(self, key):
        return key in self

    def get_many(self, keys, default=None):
        return [self.get(k, default) for k in keys]

    def set_many(self, mapping, ttl=None):
        for k, v in mapping:
            self.set(k, v, ttl)

    def delete_many(self, keys):
        return [self.delete(k) for k in keys]

    def decr(self, key, delta=1):
        return self.incr(key, -delta)
