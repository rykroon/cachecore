import os
from hashlib import md5

from cachecore.backends.base import BaseBackend
from cachecore.serializers import PickleSerializer
from cachecore.utils import Value


class FileBackend(BaseBackend):
    
    def __init__(self, dir, suffix='cache'):
        self.serializer = PickleSerializer()
        self._dir = os.path.abspath(dir)
        self._suffix = suffix
        os.makedirs(self._dir, mode=0o700, exist_ok=True)

    def _key_to_file(self, key):
        fname = md5(key.encode(), usedforsecurity=False).hexdigest()
        fname += self._suffix
        return os.path.join(self._dir, fname)

    def get(self, key):
        ...

    def set(self, key, value, ttl):
        v = Value(value, ttl)
        fname = self._key_to_file(key)
        with open(fname, 'wb') as f:
            self.serializer.dump(f)

    def add(self, key, value, ttl):
        ...

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
        ...