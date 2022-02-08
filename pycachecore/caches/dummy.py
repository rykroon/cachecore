from pycachecore.utils import MISSING_KEY


class DummyCache:

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

    def incr(self, key, delta=1):
        return delta

    def decr(self, key, delta=1):
        return -delta

    def clear(self):
        pass
