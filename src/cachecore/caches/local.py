import pickle

from .base import BaseCache
from ..utils import KEEP_TTL, is_expired, ttl_remaining, ttl_to_exptime


class LocalCache(BaseCache):

    serializer = pickle

    def __init__(self):
        self._data = {}

    def __getitem__(self, key):
        if key not in self:
            raise KeyError(key)
        value = self._data[key][0]
        return self.serializer.loads(value)

    def __setitem__(self, key, value):
        self._set(key, value, None)

    def __delitem__(self, key):
        if key not in self:
            raise KeyError(key)
        del self._data[key]

    def __contains__(self, key):
        if key not in self._data:
            return False

        expires_at = self._data[key][1]
        if is_expired(expires_at):
            del self._data[key]
            return False

        return True

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def _set(self, key, value, expires_at=None):
        value = self.serializer.dumps(value)
        self._data[key] = [value, expires_at]

    def set(self, key, value, ttl=None):
        expires_at = ttl_to_exptime(ttl)
        self._set(key, value, expires_at)

    def replace(self, key, value, ttl=KEEP_TTL):
        if key not in self:
            return False
        self._data[key][0] = self.serializer.dumps(value)
        if ttl is not KEEP_TTL:
            self._data[key][1] = ttl_to_exptime(ttl)
        return True

    def get_ttl(self, key, default=0):
        if key not in self:
            return default
        return ttl_remaining(self._data[key][1])

    def set_ttl(self, key, ttl=None):
        if not self.has_key(key):
            return False
        exp_time = ttl_to_exptime(ttl)
        self._data[key][1] = exp_time
        return True

    def incr(self, key, delta=1):
        value = self.get(key, default=0)
        value += delta
        if not self.add(key, value):
            self.replace(key, value)
        return value

        # if key not in self:
        #     value = 0
        #     ttl = None
        #     value += delta
        #     self.set(key, value, ttl)
        #     return value

        # value = self.get(key)
        # value += delta
        # self._data[key][0] = self.serializer.dumps(value)
        # return value

    def clear(self):
        self._data.clear()
