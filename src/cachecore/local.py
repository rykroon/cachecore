from dataclasses import dataclass
import pickle
from typing import Any, Optional

from .base import BaseCache
from .utils import KEEP_TTL, is_expired, ttl_remaining, ttl_to_exptime


@dataclass(slots=True)
class ExpiryValue:
    value: Any
    expires_at: Optional[float] = None

    @property
    def ttl(self):
        return ttl_remaining(self.expires_at)

    @ttl.setter
    def ttl(self, value):
        self.expires_at = ttl_to_exptime(value)

    def is_expired(self):
        return is_expired(self.expires_at)


class LocalCache(BaseCache):

    serializer = pickle

    def __init__(self):
        self._data: dict[str, ExpiryValue] = {}

    def __getitem__(self, key):
        expval = self._get(key)
        if expval is None:
            raise KeyError(key)
        return self.serializer.loads(expval.value)

    def __setitem__(self, key, value):
        self._set(key, value)

    def __delitem__(self, key):
        self._get(key) # delete key if it has expired.
        del self._data[key]

    def __contains__(self, key):
        return self._get(key) is not None

    def __iter__(self):
        for k in list(self._data.keys()):
            if self._get(k) is None:
                continue
            yield k

    def _get(self, key):
        expval = self._data.get(key)
        if expval is None:
            return None

        if expval.is_expired():
            del self._data[key]
            return None

        return expval

    def _set(self, key, value, ttl=None):
        value = self.serializer.dumps(value)
        expval = ExpiryValue(value=value)
        expval.ttl = ttl
        self._data[key] = expval

    def set(self, key, value, ttl=None):
        self._set(key, value, ttl)

    def replace(self, key, value, ttl=KEEP_TTL):
        expval = self._get(key)
        if expval is None:
            return False

        expval.value = self.serializer.dumps(value)
        if ttl is not KEEP_TTL:
            expval.ttl = ttl
        return True

    def get_ttl(self, key, default=0):
        expval = self._get(key)
        if expval is None:
            return default
        return expval.ttl

    def set_ttl(self, key, ttl=None):
        expval = self._get(key)
        if expval is None:
            return False

        expval.ttl = ttl
        return True

    def incr(self, key, delta=1):
        value = self.get(key, default=0)
        value += delta
        if not self.add(key, value):
            self.replace(key, value)
        return value

    def clear(self):
        self._data.clear()
