from collections.abc import Iterable
from fnmatch import fnmatch
from typing import Any, Optional, Protocol, runtime_checkable
from ..utils import KEEP_TTL


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

    def __iter__(self):
        ...

    def __len__(self) -> int:
        ...

    def keys(self, pattern: str = None) -> Iterable[str]:
        """
            Returns an iterable of keys that match the pattern.
        """
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """
            Returns the value assigned to the key.
            Returns default if key is not found.
        """
        ...

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
            Assign a value to a key.
            The key will expire after `ttl` seconds.
            The key will never expire if `ttl` is None.
        """
        ...

    def add(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
            Set the key only if it doesn't already exist.
        """
        ...

    def replace(self, key: str, value: Any, ttl: Optional[int] = KEEP_TTL) -> bool:
        """
            Set the key only if it already exists.
            Keeps the TTL of the previous value if a new TTL is not given.
        """
        ...

    def delete(self, key: str) -> bool:
        """
            Deletes the key.
            Returns True if a key was deleted, else False.
        """
        ...

    def pop(self, key: str, default: Any = None):
        """
            Deletes the key and returns the corresponding value.
        """
        ...

    def has_key(self, key: str) -> bool:
        ...

    def get_many(self, keys: Iterable[str], default: Any = None) -> Iterable[Any]:
        ...

    def set_many(self, mapping: Iterable[tuple[str, Any]], ttl: Optional[int] = None):
        ...

    def delete_many(self, keys: Iterable[str]) -> Iterable[bool]:
        """
            Deletes all of the keys in the list.
            Returns a list of boolean values indicating
                if the key was deleted.
        """
        ...

    def get_ttl(self, key: str, default: int = 0) -> Optional[int]:
        """
            Returns the TTL of the key.
            Returns None if key does not have a ttl.
            Returns default if the key does not exist.
        """
        ...

    def set_ttl(self, key: str, ttl: Optional[int] = None) -> bool:
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

    def __len__(self):
        return len(list(self))

    def keys(self, pattern=None):
        for key in self:
            if pattern is not None:
                if not fnmatch(key, pattern):
                    continue
            yield key

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

    def pop(self, key, default=None):
        value = self.get(key, default)
        self.delete(key)
        return value

    def has_key(self, key):
        return key in self

    def get_many(self, keys, default=None):
        return (self.get(k, default) for k in keys)

    def set_many(self, mapping, ttl=None):
        for k, v in mapping:
            self.set(k, v, ttl)

    def delete_many(self, keys):
        return (self.delete(k) for k in keys)

    def decr(self, key, delta=1):
        return self.incr(key, -delta)
