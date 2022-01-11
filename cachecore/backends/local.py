from typing import Union
from cachecore.backends.base import BaseBackend
from cachecore.serializers import PickleSerializer
from cachecore.utils import MissingKey, MissingKeyType, Value


class LocalBackend(BaseBackend):

    def __init__(self):
        self.serializer = PickleSerializer()
        self.data = {}

    def _get(self, key: str) -> Union[Value, MissingKeyType]:
        value = self.data.get(key)
        if value is None:
            return MissingKey

        value = self.serializer.loads(value)
        
        if value.is_expired():
            self._del(key)
            return MissingKey

        return value

    def _set(self, key: str, value: Value):
        self.data[key] = self.serializer.dumps(value)

    def _del(self, key: str) -> bool:
        return self.data.pop(key, MissingKey) is not MissingKey

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

    def get_many(self, *keys):
        return [self.get(k) for k in keys]

    def set_many(self, mapping, ttl):
        for k, v in mapping.items():
            self.set(k, v, ttl)

    def delete_many(self, *keys):
        return [self.delete(k) for k in keys]

    def get_ttl(self, key):
        value = self._get(key)
        if value is MissingKey:
            return 0
        return value.get_ttl()

    def set_ttl(self, key, ttl):
        value = self._get(key)
        if value is not MissingKey:
            value.set_ttl(ttl)
            self._set(key, value)

    def clear(self):
        self.data.clear()
