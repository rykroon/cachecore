from cachecore.backends.base import BaseBackend
from cachecore.singletons import MissingKey
from cachecore.serializers import RedisSerializer


class RedisBackend(BaseBackend):

    def __init__(self, serializer=None, client=None, **client_kwargs):
        self.serializer = serializer if serializer is not None else RedisSerializer()
        if client and client_kwargs:
            raise ValueError("Cannot pass a client and client kwargs.")

        if client:
            self.client = client
            return

        import redis
        self.client = redis.Redis(**client_kwargs)

    def get(self, key):
        value = self.client.get(key)
        if value is None:
            return MissingKey
        return self.serializer.loads(value)

    def set(self, key, value, ttl):
        value = self.serializer.dumps(value)
        self.client.set(key, value, ex=ttl)

    def add(self, key, value, ttl):
        value = self.serializer.dumps(value)
        return self.client.set(key, value, ex=ttl, nx=True) is not None

    def delete(self, key):
        return self.client.delete(key) != 0

    def has_key(self, key):
        return self.client.exists(key) == 1

    def get_many(self, *keys):
        values = self.client.mget(*keys)
        return [MissingKey if v is None else self.serializer.loads(v) for v in values]

    def set_many(self, mapping, ttl):
        pipeline = self.client.pipeline()
        for k, v in mapping.items():
            value = self.serializer.dumps(v)
            pipeline.set(k, value, ex=ttl)
        
        pipeline.execute()

    def delete_many(self, *keys):
        pipeline = self.client.pipeline()
        for k in keys:
            pipeline.delete(k)
        return [result == 1 for result in pipeline.execute()]

    def get_ttl(self, key):
        result = self.client.ttl(key)
        if result == -2:
            return 0

        if result == -1:
            return None

        return result

    def set_ttl(self, key, ttl):
        if ttl is None:
            self.client.persist(key)
        else:
            self.client.expire(key, ttl)

    def clear(self):
        self.client.flushdb()
