import pickle
from typing import Union

from cachecore.utils import MISSING_KEY, is_expired, \
    ttl_remaining, ttl_to_exptime


class LocalCache:

    serializer = pickle

    def __init__(self):
        self._data = {}

    def _read(self, key, exclude_value=False):
        if key not in self._data:
            return MISSING_KEY, MISSING_KEY

        value, expires_at = self._data[key]
        if is_expired(expires_at):
            del self._data[key]
            return MISSING_KEY, MISSING_KEY

        ttl = ttl_remaining(expires_at)
        if exclude_value:
            return MISSING_KEY, ttl

        value = self.serializer.loads(value)
        return value, ttl

    def _write(self, key, value, ttl):
        value = self.serializer.dumps(value)
        exp_time = ttl_to_exptime(ttl)
        self._data[key] = [value, exp_time]

    def get(self, key):
        value, _ = self._read(key)
        return value

    def set(self, key, value, ttl=None):
        self._write(key, value, ttl)

    def add(self, key, value, ttl=None):
        if self.has_key(key):
            return False
        self.set(key, value, ttl)
        return True

    def delete(self, key):
        if not self.has_key(key):
            return False 
        del self._data[key]
        return True

    def has_key(self, key):
        _, ttl = self._read(key, exclude_value=True)
        return ttl is not MISSING_KEY

    def get_many(self, *keys):
        return [self.get(k) for k in keys]

    def set_many(self, mapping, ttl=None):
        for k, v in mapping:
            self.set(k, v, ttl)

    def delete_many(self, *keys):
        return [self.delete(k) for k in keys]

    def get_ttl(self, key):
        _, ttl = self._read(key, exclude_value=True)
        return ttl

    def set_ttl(self, key, ttl=None):
        if not self.has_key(key):
            return
        exp_time = ttl_to_exptime(ttl)
        self._data[key][1] = exp_time

    def incr(self, key, delta=1):
        value, ttl = self._read(key)
        if value is MISSING_KEY:
            value = 0
            ttl = None

        value += delta
        self._write(key, value, ttl)
        return value

    def decr(self, key, delta=1):
        return self.incr(key, -delta)

    def clear(self):
        self._data.clear()
