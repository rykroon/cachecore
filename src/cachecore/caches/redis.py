from cachecore.serializers import RedisSerializer
from cachecore.utils import MISSING_KEY


class RedisCache:

    serializer = RedisSerializer()

    def __init__(self, client=None, **client_kwargs):
        if client and client_kwargs:
            raise ValueError("Cannot pass a client and client kwargs.")

        if client:
            self._client = client
            return

        import redis
        self._client = redis.Redis(**client_kwargs)

    def __getitem__(self, key):
        value = self._client.get(key)
        if value is None:
            raise KeyError(key)
        return self.serializer.loads(value)

    def __setitem__(self, key, value):
        ttl = None
        if isinstance(value, tuple):
            if len(value) == 2:
                value, ttl = value
        value = self.serializer.dumps(value)
        self._client.set(key, value, ex=ttl)

    def __delitem__(self, key):
        result = bool(self._client.delete(key))
        if not result:
            raise KeyError(key)

    def __contains__(self, key):
        return bool(self._client.exists(key))

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def set(self, key, value, ttl=None):
        self[key] = value, ttl

    def add(self, key, value, ttl=None):
        value = self.serializer.dumps(value)
        return self._client.set(key, value, ex=ttl, nx=True) is not None

    def delete(self, key):
        try:
            del self[key]
            return True
        except KeyError:
            return False

    def has_key(self, key):
        return key in self

    def get_many(self, keys):
        values = self._client.mget(*keys)
        return [None if v is None else self.serializer.loads(v) for v in values]

    def set_many(self, mapping, ttl=None):
        pipeline = self._client.pipeline()
        for k, v in mapping:
            value = self.serializer.dumps(v)
            pipeline.set(k, value, ex=ttl)

        pipeline.execute()

    def delete_many(self, keys):
        pipeline = self._client.pipeline()
        for k in keys:
            pipeline.delete(k)
        return [bool(result) for result in pipeline.execute()]

    def get_ttl(self, key):
        result = self._client.ttl(key)
        if result == -2:
            return MISSING_KEY

        if result == -1:
            return None

        return result

    def set_ttl(self, key, ttl=None):
        if ttl is None:
            self._client.persist(key)
        else:
            self._client.expire(key, ttl)

    def incr(self, key, delta=1):
        return self._client.incr(key, delta)

    def decr(self, key, delta=1):
        return self._client.decr(key, delta)

    def clear(self):
        self._client.flushdb()
