import os
from hashlib import md5

from cachecore.serializers import PickleSerializer
from cachecore.utils import MISSING_KEY, Value


class FileBackend:
    
    def __init__(self, dir, ext='.cachecore'):
        self.serializer = PickleSerializer()
        self._dir = os.path.abspath(dir)
        self._ext = ext
        os.makedirs(self._dir, mode=0o700, exist_ok=True)

    def _key_to_file(self, key):
        fname = md5(key.encode(), usedforsecurity=False).hexdigest()
        fname += self._ext
        return os.path.join(self._dir, fname)

    def _read_value(self, key):
        fname = self._key_to_file(key)
        try:
            with open(fname, 'rb') as f:
                value = self.serializer.load(f)
                if value.is_expired():
                    # delete file
                    return MISSING_KEY
                return value

        except FileNotFoundError:
            return MISSING_KEY

    def _write_value(self, key, value):
        fname = self._key_to_file(key)
        with open(fname, 'wb') as f:
            self.serializer.dump(value, f)

    def get(self, key):
        value = self._read_value(key)
        if value is MISSING_KEY:
            return MISSING_KEY
        return value.value

    def set(self, key, value, ttl):
        self._write_value(key, Value(value, ttl))

    def add(self, key, value, ttl):
        if self.has_key(key):
            return False
        self.set(key, value, ttl)
        return True

    def delete(self, key):
        fname = self._key_to_file(key)
        if not os.path.exists(fname):
            return False
        
        try:
            os.remove(fname)
        except FileNotFoundError:
            return False
        return True

    def has_key(self, key):
        fname = self._key_to_file(key)
        return os.path.isfile(fname)

    def get_many(self, *keys):
        return [self.get(k) for k in keys]

    def set_many(self, mapping, ttl):
        for k, v in mapping.items():
            self.set(k, v, ttl)

    def delete_many(self, *keys):
        return [self.delete(k) for k in keys]

    def get_ttl(self, key):
        value = self._read_value(key)
        if value is MISSING_KEY:
            return 0
        return value.get_ttl()

    def set_ttl(self, key, ttl):
        value = self._read_value(key)
        if value is not MISSING_KEY:
            value.set_ttl(ttl)
            self._write_value(key, value)

    def incrby(self, key, delta):
        ...

    def decrby(self, key, delta):
        ...

    def clear(self):
        ...