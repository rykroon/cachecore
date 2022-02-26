import pickle

from cachecore.caches import BaseCache
from cachecore.utils import MISSING_KEY, is_expired, \
    ttl_remaining, ttl_to_exptime


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
        ttl = None
        if isinstance(value, tuple):
            if len(value) == 2:
                value, ttl = value

        value = self.serializer.dumps(value)
        exp_time = ttl_to_exptime(ttl)
        self._data[key] = [value, exp_time]

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

    def set(self, key, value, ttl=None):
        self[key] = value, ttl

    def get_ttl(self, key):
        if key not in self:
            return MISSING_KEY
        return ttl_remaining(self._data[key][1])

    def set_ttl(self, key, ttl=None):
        if not self.has_key(key):
            return
        exp_time = ttl_to_exptime(ttl)
        self._data[key][1] = exp_time

    def incr(self, key, delta=1):
        if key not in self:
            value = 0
            ttl = None
            value += delta
            self.set(key, value, ttl)
            return value

        value = self.get(key)
        value += delta
        self._data[key][0] = self.serializer.dumps(value)
        return value

    def clear(self):
        self._data.clear()
