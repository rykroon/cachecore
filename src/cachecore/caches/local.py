import pickle

from cachecore.utils import MISSING_KEY, is_expired, \
    ttl_remaining, ttl_to_exptime


class LocalCache:

    serializer = pickle

    def __init__(self):
        self._data = {}

    def _read(self, key, incttl=False, incval=False):
        if incval:
            incttl = True

        if key not in self._data:
            return False, None, None

        value, expires_at = self._data[key]
        if is_expired(expires_at):
            del self._data[key]
            return False, None, None

        if not incttl:
            return True, None, None

        ttl = ttl_remaining(expires_at)
        if not incval:
            return True, ttl, None

        value = self.serializer.loads(value)
        return True, ttl, value

    def _write(self, key, value, ttl):
        value = self.serializer.dumps(value)
        exp_time = ttl_to_exptime(ttl)
        self._data[key] = [value, exp_time]

    def get(self, key):
        exists, _, value = self._read(key, incval=True)
        if not exists:
            return MISSING_KEY
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
        exists, _, _ = self._read(key)
        return exists

    def get_many(self, *keys):
        return [self.get(k) for k in keys]

    def set_many(self, mapping, ttl=None):
        for k, v in mapping:
            self.set(k, v, ttl)

    def delete_many(self, *keys):
        return [self.delete(k) for k in keys]

    def get_ttl(self, key):
        exists, ttl, _ = self._read(key, incttl=True)
        if not exists:
            return MISSING_KEY
        return ttl

    def set_ttl(self, key, ttl=None):
        if not self.has_key(key):
            return
        exp_time = ttl_to_exptime(ttl)
        self._data[key][1] = exp_time

    def incr(self, key, delta=1):
        exists, ttl, value = self._read(key, incval=True)
        if not exists:
            value = 0
            ttl = None

        value += delta
        self._write(key, value, ttl)
        return value

    def decr(self, key, delta=1):
        return self.incr(key, -delta)

    def clear(self):
        self._data.clear()
