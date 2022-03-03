from cachecore.serializers import RedisSerializer


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
        value = self.serializer.dumps(value)
        self._client.set(key, value)

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
        value = self.serializer.dumps(value)
        self._client.set(key, value, ex=ttl)

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

    def get_many(self, keys, default=None):
        values = self._client.mget(*keys)
        return [default if v is None else self.serializer.loads(v) for v in values]

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

    def get_ttl(self, key, default=0):
        result = self._client.ttl(key)
        if result == -2:
            return default

        if result == -1:
            return None

        return result

    def set_ttl(self, key, ttl=None):
        if ttl is None:
            pipeline = self._client.pipeline()
            # persist returns False if either the key does not exist
            # OR if the key is already persisted. So we need to return 
            # the result of exists.
            pipeline.persist(key) 
            pipeline.exists(key)
            _, exists = pipeline.execute()
            return bool(exists)

        return bool(self._client.expire(key, ttl))

    def incr(self, key, delta=1):
        return self._client.incr(key, delta)

    def decr(self, key, delta=1):
        return self._client.decr(key, delta)

    def clear(self):
        self._client.flushdb()
