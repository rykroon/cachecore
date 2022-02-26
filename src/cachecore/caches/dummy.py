from cachecore.utils import MISSING_KEY
from cachecore.caches import BaseCache


class DummyCache(BaseCache):

    def __getitem__(self, key):
        raise KeyError(key)

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        raise KeyError(key)

    def __contains__(self, key):
        return False

    def set(self, key, value, ttl=None):
        pass

    def get_ttl(self, key):
        return MISSING_KEY

    def set_ttl(self, key, ttl=None):
        pass

    def incr(self, key, delta=1):
        return delta

    def clear(self):
        pass
