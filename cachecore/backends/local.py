from cachecore.backends.base import BaseBackend
from cachecore.serializers import PickleSerializer
from cachecore.utils import MissingKey, Value


class LocalBackend(BaseBackend):

    def __init__(self):
        self.serializer = PickleSerializer()
        self.data = {}

    def _get_value(self, key):
        value = self.data.get(key)
        if value is None:
            return MissingKey

        value = self.serializer.loads(value)
        
        if value.is_expired():
            del self.data[key]
            return MissingKey

        return value

    def get(self, key):
        value = self._get_value(key)
        if value is MissingKey:
            return MissingKey
        return self.serializer.loads(value.value)

    def set(self, key, value, ttl):
        self.data[key] = self.serializer.dumps(Value(value, ttl))

    def add(self, key, value, ttl):
        if self.has_key(key):
            return False
        self.set(key, value, ttl)
        return True

    def delete(self, key):
        value = self._get_value(key)
        if value is MissingKey:
            return False

        del self.data[key]
        return True

    def has_key(self, key):
        value = self._get_value(key)
        return value is not MissingKey

    def get_many(self, *keys):
        return [self.get(k) for k in keys]

    def set_many(self, mapping, ttl):
        for k, v in mapping.items():
            self.set(k, v, ttl)

    def delete_many(self, *keys):
        return [self.delete(k) for k in keys]

    def get_ttl(self, key):
        value = self._get_value(key)
        if value is MissingKey:
            return 0
        return value.get_ttl()

    def set_ttl(self, key, ttl):
        value = self._get_value(key)
        if value is not MissingKey:
            value.set_ttl(ttl)

    def clear(self):
        self.data.clear()
