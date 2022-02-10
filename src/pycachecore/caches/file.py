from hashlib import md5
import pickle

from pycachecore.utils import MISSING_KEY, Value, Directory


class FileCache:
    
    def __init__(self, dir, ext='.cachecore'):
        self.serializer = pickle
        self._dir = Directory(dir)
        self._ext = ext

    def _key_to_file(self, key):
        fname = md5(key.encode(), usedforsecurity=False).hexdigest()
        fname += self._ext
        return fname

    def _get_value(self, key):
        fname = self._key_to_file(key)
        try:
            value = self._dir[fname]
        except KeyError:
            return MISSING_KEY
        
        value = self.serializer.loads(value)
        if value.is_expired():
            del self._dir[fname]
            return MISSING_KEY

        return value

    def _set_value(self, key, value):
        fname = self._key_to_file(key)
        self._dir[fname] = self.serializer.dumps(value)

    def get(self, key):
        value = self._get_value(key)
        if value is MISSING_KEY:
            return MISSING_KEY
        return value.value

    def set(self, key, value, ttl=None):
        value = Value(value, ttl)
        self._set_value(key, value)

    def add(self, key, value, ttl=None):
        if self.has_key(key):
            return False
        self.set(key, value, ttl)
        return True

    def delete(self, key):
        fname = self._key_to_file(key)
        try:
            del self._dir[fname]
        except KeyError:
            return False

        return True

    def has_key(self, key):
        return self._get_value(key) is not MISSING_KEY

    def get_many(self, *keys):
        return [self.get(k) for k in keys]

    def set_many(self, mapping, ttl=None):
        for k, v in mapping:
            self.set(k, v, ttl)

    def delete_many(self, *keys):
        return [self.delete(k) for k in keys]

    def get_ttl(self, key):
        value = self._get_value(key)
        if value is MISSING_KEY:
            return MISSING_KEY
        return value.get_ttl()

    def set_ttl(self, key, ttl=None):
        value = self._get_value(key)
        if value is not MISSING_KEY:
            value.set_ttl(ttl)
            self._set_value(key, value)

    def incr(self, key, delta=1):
        value = self._get_value(key)
        if value is MISSING_KEY:
            value = Value(0, None)

        value.value += delta
        self._set_value(key, value)
        return value.value

    def decr(self, key, delta=1):
        return self.incr(key, -delta)

    def clear(self):
        for path in self._dir:
            if not path.is_file():
                continue
                
            if not path.name.endswith(self._ext):
                continue

            path.unlink(missing_ok=True)
