import pickle
from typing import Union

from pycachecore.utils import MissingKey, MISSING_KEY, Value


class LocalCache:

    def __init__(self):
        self.serializer = pickle
        self._data = {}

    def _get_value(self, key: str) -> Union[Value, MissingKey]:
        value = self._data.get(key)
        if value is None:
            return MISSING_KEY

        value = self.serializer.loads(value)
        
        if value.is_expired():
            self.delete(key)
            return MISSING_KEY

        return value

    def _set_value(self, key: str, value: Value):
        self._data[key] = self.serializer.dumps(value)        

    def get(self, key):
        value = self._get_value(key)
        if value is MISSING_KEY:
            return MISSING_KEY
        return value.value

    def set(self, key, value, ttl=None):
        self._set_value(key, Value(value, ttl))

    def add(self, key, value, ttl=None):
        if self.has_key(key):
            return False
        self.set(key, value, ttl)
        return True

    def delete(self, key):
        return self._data.pop(key, MISSING_KEY) is not MISSING_KEY

    def has_key(self, key):
        value = self._get_value(key)
        return value is not MISSING_KEY

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
        self._data.clear()
