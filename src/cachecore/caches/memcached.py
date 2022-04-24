from cachecore.utils import KEEP_TTL
from .base import BaseCache
from ..serializers import RedisSerializer


class MemcachedCache(BaseCache):

    serializer = RedisSerializer()

    def __init__(self, client=None, **client_kwargs):
        if client and client_kwargs:
            raise ValueError("Cannot pass a client and client kwargs.")

        if client:
            self._client = client
            return

        import pymemcache
        self._client = pymemcache.client.Client(**client_kwargs)

    def __getitem__(self, key):
        value = self._client.get(key)
        if value is None:
            raise KeyError(key)
        return self.serializer.loads(value)

    def __setitem__(self, key, value):
        value = self.serializer.dumps(value)
        self._client.set(key, value)

    def __delitem__(self, key):
        if key not in self:
            raise KeyError(key)
        self._client.delete(key)

    def __contains__(self, key):
        return self._client.get(key) is not None

    def __iter__(self):
        raise NotImplementedError

    def keys(self, pattern=None):
        raise NotImplementedError

    def set(self, key, value, ttl=None):
        value = self.serializer.dumps(value)
        if ttl is None:
            ttl = 0
        self._client.set(key, value, expire=ttl)

    def replace(self, key, value, ttl=KEEP_TTL):
        if ttl is KEEP_TTL:
            raise NotImplementedError('Cannot keep TTL with Memcached backend.')

        if key not in self:
            return False

        if ttl is None:
            ttl = 0

        self._client.replace(key, value, expire=ttl)
        return True

    def get_ttl(self, key, default=0):
        raise NotImplementedError

    def set_ttl(self, key, ttl=None):
        raise NotImplementedError

    def incr(self, key, delta=1):
        # Memcached does not accept negative values.
        if delta < 0:
            return self.decr(abs(delta))

        # Add an initial value of 0 if there isn't already a value since
        # incr/decr will fail if there isn't already a value.
        self.add(key, 0)
        return self._client.incr(key, delta)

    def decr(self, key, delta=1):
        # Memcached does not accept negative values.
        if delta < 0:
            return self.incr(abs(delta))
        
        # Because memcached will not decrement the value below zero we
        # need to manually update the value.
        value = self.get(key, 0)
        value -= delta
        self.set(key, value)
        return value

    def clear(self):
        self._client.flush_all()
    