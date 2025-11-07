from collections.abc import MutableMapping
from dataclasses import dataclass, field, InitVar
from functools import cache
from math import ceil
import time
from typing import Any


_missing_key = object()


@dataclass(slots=True)
class ExpiryValue:
    value: Any
    ttl: InitVar[int | None]
    expires_at: float = field(init=False)

    def __post_init__(self, ttl: int | None):
        self.ttl = ttl
    
    def __repr__(self):
        return "EXPIRED" if self.is_expired() else repr(self.value)

    @property
    def ttl(self) -> int | None:
        if self.expires_at == float("inf"):
            return None
        return max(0, ceil(self.expires_at - time.time()))

    @ttl.setter
    def ttl(self, ttl: int | None):
        expiry = float("inf") if ttl is None else ttl
        self.expires_at = time.time() + expiry

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class ExpiryDict(MutableMapping[str, ExpiryValue]):

    def __init__(self):
        self._data: dict[str, ExpiryValue] = {}

    def __repr__(self):
        return repr(self._data)

    def __getitem__(self, key):
        item = self._data.get(key)
        if item is None or item.is_expired():
            self._data.pop(key, None)
            raise KeyError(key)
        return item.value

    def set(self, key: str, value: Any, ttl: int | None = None):
        self[key] = ExpiryValue(value, ttl)

    def __setitem__(self, key: str, item: ExpiryValue):
        self._data[key] = item

    def __delitem__(self, key: str):
        key in self # removes key if expired
        del self._data[key]

    def __iter__(self):
        for key in list(self._data.keys()):
            if key in self:
                yield key

    def __len__(self):
        list(iter(self)) # Remove all expired keys
        return len(self._data)


class Singleton:
    @cache
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)


class KeepTTL(Singleton):
    ...


KEEP_TTL = KeepTTL()
