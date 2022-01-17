import pickle
from typing import Union

from cachecore.utils import MissingKey, MISSING_KEY, Value


class LocalBackend:

    """
        IDEA! Define a lower lower level API with the following methods:
            - _read
            - _write
            - _delete
        All other methods can be accomplished using these methods.
        In scenarios where relying on the default logic isn't best, 
            just override the method.
    """


    def __init__(self):
        self.serializer = pickle
        self._data = {}

    def _read_value(self, key: str) -> Union[Value, MissingKey]:
        value = self._data.get(key)
        if value is None:
            return MISSING_KEY

        value = self.serializer.loads(value)
        
        if value.is_expired():
            self._del(key)
            return MISSING_KEY

        return value

    def _write_value(self, key: str, value: Value):
        self._data[key] = self.serializer.dumps(value)        

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
        return self._data.pop(key, MISSING_KEY) is not MISSING_KEY

    def has_key(self, key):
        value = self._read_value(key)
        return value is not MISSING_KEY

    def get_many(self, *keys):
        return [self.get(k) for k in keys]

    def set_many(self, mapping, ttl):
        for k, v in mapping:
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
        self._data.clear()
