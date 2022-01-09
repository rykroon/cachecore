from math import ceil
import time
from cache.backends.base import BaseBackend
from cache.constants import MissingKey
from cache.serializers import PassthroughSerializer


class LocalValue:
    def __init__(self, value, ttl):
        self.value = value
        self.set_ttl(ttl)

    def get_ttl(self):
        if self.expires_at is None:
            return None

        return max(0, ceil(self.expires_at - time.time()))

    def set_ttl(self, ttl):
        self.expires_at = None if ttl is None else time.time() + ttl

    def is_expired(self):
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


class LocalBackend(BaseBackend):

    def __init__(self, serializer=None):
        self.serializer = serializer if serializer is not None else PassthroughSerializer()
        self.data = {}

    def _get_value(self, key):
        value = self.data.get(key)
        if value is None:
            return MissingKey
        
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
        value = self.serializer.dumps(value)
        self.data[key] = LocalValue(value, ttl)

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
