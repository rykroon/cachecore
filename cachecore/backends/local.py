from typing import Union
from cachecore.backends.base import BaseBackend
from cachecore.serializers import PickleSerializer
from cachecore.utils import MissingKey, MissingKeyType, Value


class LocalBackend(BaseBackend):

    def __init__(self):
        self.serializer = PickleSerializer()
        self._data = {}

    def _read_value(self, key: str) -> Union[Value, MissingKeyType]:
        value = self._data.get(key)
        if value is None:
            return MissingKey

        value = self.serializer.loads(value)
        
        if value.is_expired():
            self._del(key)
            return MissingKey

        return value

    def _write_value(self, key: str, value: Value):
        self._data[key] = self.serializer.dumps(value)        

    def get(self, key):
        value = self._read_value(key)
        if value is MissingKey:
            return MissingKey
        return value.value

    def set(self, key, value, ttl):
        self._write_value(key, Value(value, ttl))

    def add(self, key, value, ttl):
        if self.has_key(key):
            return False
        self.set(key, value, ttl)
        return True

    def delete(self, key):
        return self._data.pop(key, MissingKey) is not MissingKey

    def has_key(self, key):
        value = self._read_value(key)
        return value is not MissingKey

    def get_many(self, *keys):
        return [self.get(k) for k in keys]

    def set_many(self, mapping, ttl):
        for k, v in mapping.items():
            self.set(k, v, ttl)

    def delete_many(self, *keys):
        return [self.delete(k) for k in keys]

    def get_ttl(self, key):
        value = self._read_value(key)
        if value is MissingKey:
            return 0
        return value.get_ttl()

    def set_ttl(self, key, ttl):
        value = self._read_value(key)
        if value is not MissingKey:
            value.set_ttl(ttl)
            self._write_value(key, value)

    def clear(self):
        self._data.clear()
