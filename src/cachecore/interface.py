import typing as t
from .utils import KEEP_TTL


@t.runtime_checkable
class CacheInterface(t.Protocol):

    def __getitem__(self, key: str) -> t.Any:
        ...

    def __setitem__(self, key: str, value: t.Any):
        ...

    def __delitem__(self, key: str):
        ...

    def __contains__(self, key: str):
        ...

    def __iter__(self):
        ...

    def __len__(self) -> int:
        ...

    def keys(self, pattern: str | None = None) -> t.Iterable[str]:
        """Returns an iterable of keys that match the pattern.
        
        :param pattern: The pattern to be matched.
        :returns: An iterable of keys that match the pattern.
        """
        ...

    def get(self, key: str, default: t.Any = None) -> t.Any:
        """Returns the value associated with the key.
        
        :param key: The key to be retrieved.
        :param default: The default value if the key is not found.
        :returns: The value associated with the key.
        """
        ...

    def set(self, key: str, value: t.Any, ttl: int | None = None):
        """Assign a value to a key.

        :param key: The key to be set.
        :param value: The value to be stored.
        :param ttl: The time-to-live. If None, then the value will not expire.
        """
        ...

    def add(self, key: str, value: t.Any, ttl: int | None = None) -> bool:
        """Set the value only if the key doesn't already exist.

        :param key: The key to be set.
        :param value: The value to be stored.
        :param ttl: The time-to-live.
        :returns: True, if the key was added, else False.
        """
        ...

    def replace(self, key: str, value: t.Any, ttl: int | None = KEEP_TTL) -> bool:
        """Set the value only if the key already exists.
        
        :param key: The key to be set.
        :param value: The value to be stored.
        :param ttl: The time-to-live. By default, it will keep the ttl.
        :returns: True, if the key was added, else False.
        """
        ...

    def delete(self, key: str) -> bool:
        """Delete the key.
        
        :param key: The key to be deleted.
        :returns: True, if the key was deleted, else False.
        """
        ...

    def pop(self, key: str, default: t.Any = None):
        """Deletes the key and returns the associated value.

        :param key: The key to be deleted.
        :param default: The value to be returned if the key does not exist.
        :returns: The value associated with the key, or the default.
        """
        ...

    def exists(self, key: str) -> bool:
        """Returns whether or not the key exists.

        :param key: The key to check.
        :returns: True, if the key exists, else False.
        """
        ...

    def get_many(self, keys: t.Iterable[str], default: t.Any = None) -> t.Iterable[t.Any]:
        """Returns an iterable of values.

        :param keys: An iterable of keys to retrieve.
        :param default: A default value in case a key is not found.
        :returns: An iterable of values.
        """
        ...

    def set_many(self, mapping: t.Iterable[tuple[str, t.Any]], ttl: int | None = None):
        """Stores the mapping of key value pairs.

        :param mapping: An iterable of key, value tuples.
        :param ttl: The time-to-live.
        """
        ...

    def delete_many(self, keys: t.Iterable[str]) -> t.Iterable[bool]:
        """Deletes all of the keys in the iterable.

        :param keys: An iterable of keys to be deleted.
        :returns: An iterable of boolean values indicating if the key was deleted.
        """
        ...

    def get_ttl(self, key: str, default: int = 0) -> int | None:
        """Returns the TTL of the key.

        :param key: The key.
        :param default: The default value to return if the key does not exist.
        :returns: The time-to-live.
        """
        ...

    def set_ttl(self, key: str, ttl: int | None = None) -> bool:
        """Sets the TTL of the key.

        :param key: The key.
        :param ttl: The time-to-live.
        :returns: True, if the TTL was updated, else False.
        """
        ...

    def incr(self, key, delta=1) -> int:
        """Increment the value associated with the key.
        Creates the key if it does not exist.

        :param key: The key.
        :param delta: The amount to increment.
        :returns: The amount.
        """
        ...

    def decr(self, key, delta=1) -> int:
        """Decrement the value associated with the key.
        Creates the key if it does not exist.

        :param key: The key.
        :param delta: The amount to decrement.
        :returns: The amount.
        """
        ...

    def clear(self):
        """Clears all keys in the cache.
        """
        ...