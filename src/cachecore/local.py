import pickle
import typing as t

from .base import BaseCache
from .utils import KEEP_TTL, ExpiryValue


class LocalCache(BaseCache):

    serializer = pickle

    def __init__(self):
        self._data: dict[str, ExpiryValue] = {}

    def __getitem__(self, key: str) -> t.Any:
        expval = self._get(key)
        if expval is None:
            raise KeyError(key)
        return self.serializer.loads(expval.value)

    def __setitem__(self, key: str, value: t.Any):
        self._set(key, value)

    def __delitem__(self, key: str) -> None:
        self._get(key) # delete key if it has expired.
        del self._data[key]

    def __contains__(self, key: str) -> bool:
        return self._get(key) is not None

    def __iter__(self) -> t.Iterable:
        for k, v in tuple(self._data.items()):
            if v.is_expired():
                del self._data[k]
                continue
            yield k

    def _get(self, key: str):
        expval = self._data.get(key)
        if expval is None:
            return None

        if expval.is_expired():
            del self._data[key]
            return None

        return expval

    def _set(self, key: str, value: t.Any, ttl: int | None = None) -> None:
        value = self.serializer.dumps(value)
        expval = ExpiryValue(value=value)
        expval.ttl = ttl
        self._data[key] = expval

    def set(self, key: str, value: t.Any, ttl: int | None = None):
        self._set(key, value, ttl)

    def replace(self, key: str, value: int | None, ttl: int | None = KEEP_TTL):
        expval = self._get(key)
        if expval is None:
            return False

        expval.value = self.serializer.dumps(value)
        if ttl is not KEEP_TTL:
            expval.ttl = ttl
        return True

    def get_ttl(self, key: str, default: int = 0) -> int:
        expval = self._get(key)
        if expval is None:
            return default
        return expval.ttl

    def set_ttl(self, key: str, ttl: int | None = None) -> bool:
        expval = self._get(key)
        if expval is None:
            return False

        expval.ttl = ttl
        return True

    def incr(self, key: str, delta: int = 1) -> int:
        value = self.get(key, default=0)
        value += delta
        if not self.add(key, value):
            self.replace(key, value)
        return value

    def clear(self) -> None:
        self._data.clear()
