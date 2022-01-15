from cachecore.backends.base import BaseBackend
from cachecore.serializers import RedisSerializer
from cachecore.utils import MissingKey


class RedisBackend(BaseBackend):

    def __init__(self, serializer=None, client=None, **client_kwargs):
        self.serializer = serializer if serializer is not None else RedisSerializer()
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
            return MissingKey
        return self.serializer.loads(value)

    def set(self, key, value, ttl):
        value = self.serializer.dumps(value)
        self._client.set(key, value, ex=ttl)

    def add(self, key, value, ttl):
        value = self.serializer.dumps(value)
        return self._client.set(key, value, ex=ttl, nx=True) is not None

    def delete(self, key):
        return self._client.delete(key) != 0

    def has_key(self, key):
        return self._client.exists(key) == 1

    def get_many(self, *keys):
        values = self._client.mget(*keys)
        return [MissingKey if v is None else self.serializer.loads(v) for v in values]

    def set_many(self, mapping, ttl):
        pipeline = self._client.pipeline()
        for k, v in mapping.items():
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
            return 0

        if result == -1:
            return None

        return result

    def set_ttl(self, key, ttl):
        if ttl is None:
            self._client.persist(key)
        else:
            self._client.expire(key, ttl)

    def clear(self):
        self._client.flushdb()
