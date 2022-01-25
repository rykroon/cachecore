from cachecore.utils import MISSING_KEY


class DummyBackend:

    def get(self, key):
        return MISSING_KEY

    def set(self, key, value, ttl=None):
        pass

    def add(self, key, value, ttl=None):
        return False

    def delete(self, key):
        return False

    def has_key(self, key):
        return False

    def get_many(self, *keys):
        return [MISSING_KEY] * len(keys)

    def set_many(self, mapping, ttl=None):
        pass

    def delete_many(self, *keys):
        return [False] * len(keys)

    def get_ttl(self, key):
        return MISSING_KEY

    def set_ttl(self, key, ttl=None):
        pass

    def incrby(self, key, delta):
        ...

    def decrby(self, key, delta):
        ...

    def clear(self):
        pass
