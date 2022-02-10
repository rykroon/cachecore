from pycachecore.serializers import RedisSerializer
from pycachecore.utils import MISSING_KEY


class RedisCache:

    def __init__(self, client=None, **client_kwargs):
        self.serializer = RedisSerializer()
        if client and client_kwargs:
            raise ValueError("Cannot pass a client and client kwargs.")

        if client:
            self._client = client
            return

        import redis
        self._client = redis.Redis(**client_kwargs)

    def get(self, key):
        value = self._client.get(key)
        if value is None:
            return MISSING_KEY
        return self.serializer.loads(value)

    def set(self, key, value, ttl=None):
        value = self.serializer.dumps(value)
        self._client.set(key, value, ex=ttl)

    def add(self, key, value, ttl=None):
        value = self.serializer.dumps(value)
        return self._client.set(key, value, ex=ttl, nx=True) is not None

    def delete(self, key):
        return self._client.delete(key) != 0

    def has_key(self, key):
        return self._client.exists(key) == 1

    def get_many(self, *keys):
        values = self._client.mget(*keys)
        return [MISSING_KEY if v is None else self.serializer.loads(v) for v in values]

    def set_many(self, mapping, ttl=None):
        pipeline = self._client.pipeline()
        for k, v in mapping:
            value = self.serializer.dumps(v)
            pipeline.set(k, value, ex=ttl)
        
        pipeline.execute()

    def delete_many(self, *keys):
        pipeline = self._client.pipeline()
        for k in keys:
            pipeline.delete(k)
        return [result == 1 for result in pipeline.execute()]

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
