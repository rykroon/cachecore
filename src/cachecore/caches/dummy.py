from .base import BaseCache
from ..utils import KEEP_TTL


class DummyCache(BaseCache):

    def __getitem__(self, key):
        raise KeyError(key)

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        raise KeyError(key)

    def __contains__(self, key):
        return False

    def __iter__(self):
        return iter([])

    def set(self, key, value, ttl=None):
        pass

    def replace(self, key, value, ttl=KEEP_TTL):
        return False

    def get_ttl(self, key, default=0):
        return default

    def set_ttl(self, key, ttl=None):
        return False

    def incr(self, key, delta=1):
        return delta

    def clear(self):
        pass
