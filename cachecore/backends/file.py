import os
from hashlib import md5

from cachecore.backends.base import BaseBackend
from cachecore.serializers import PickleSerializer
from cachecore.utils import MissingKey, Value


class FileBackend(BaseBackend):

    ext = '.cachecore'
    
    def __init__(self, dir):
        self.serializer = PickleSerializer()
        self._dir = os.path.abspath(dir)
        os.makedirs(self._dir, mode=0o700, exist_ok=True)

    def _key_to_file(self, key):
        fname = md5(key.encode(), usedforsecurity=False).hexdigest()
        fname += self.ext
        return os.path.join(self._dir, fname)

    def _get(self, key):
        fname = self._key_to_file(key)
        try:
            with open(fname, 'rb') as f:
                value = self.serializer.load(f)
                if value.is_expired():
                    # delete file
                    return MissingKey
                return value

        except FileNotFoundError:
            return MissingKey

    def _set(self, key, value):
        fname = self._key_to_file(key)
        with open(fname, 'wb') as f:
            self.serializer.dump(value, f)

    def _del(self, key):
        fname = self._key_to_file(key)
        if not os.path.exists(fname):
            return False
        
        try:
            os.remove(fname)
        except FileNotFoundError:
            return False
        return True

    def get(self, key):
        value = self._get(key)
        if value is MissingKey:
            return MissingKey
        return value.value

    def set(self, key, value, ttl):
        self._set(key, Value(value, ttl))

    def add(self, key, value, ttl):
        if self.has_key(key):
            return False
        self.set(key, value, ttl)
        return True

    def delete(self, key):
        return self._del(key)

    def has_key(self, key):
        value = self._get(key)
        return value is not MissingKey