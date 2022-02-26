import pickle

from cachecore.caches import BaseCache
from cachecore.utils import is_expired, ttl_remaining, ttl_to_exptime


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
        value = self.serializer.dumps(value)
        self._data[key] = [value, None]

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
        value = self.serializer.dumps(value)
        exp_time = ttl_to_exptime(ttl)
        self._data[key] = [value, exp_time]

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
