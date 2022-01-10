from cachecore.backends.base import BaseBackend
from cachecore.singletons import MissingKey


class DummyBackend(BaseBackend):

    def get(self, key):
        return MissingKey

    def set(self, key, value, ttl):
        pass

    def add(self, key, value, ttl):
        return False

    def delete(self, key):
        return False

    def has_key(self, key):
        return False

    def get_many(self, *keys):
        return [MissingKey] * len(keys)

    def set_many(self, mapping, ttl):
        pass

    def delete_many(self, *keys):
        return [False] * len(keys)

    def get_ttl(self, key):
        return 0

    def set_ttl(self, key, ttl):
        pass

    def clear(self):
        pass
