from cachecore.serializers import PickleSerializer

_default = object()


class RedisDict(dict):

    def __init__(self, client):
        self._client = client
        self._serializer = PickleSerializer()

    def __getitem__(self, key):
        result = self._client.get(key)
        if result is None:
            raise KeyError(key)
        return self._serializer.loads(result)

    def __setitem__(self, key, value):
        value = self._serializer.dumps(value)
        self._client.set(key, value)

    def __delitem__(self, key):
        result = self._client.delete(key)
        if not result:
            raise KeyError(key)

    def __contains__(self, key):
        return self.exists(key) == 1

    def clear(self):
        self._client.flushdb()

    def copy(self):
        ...

    @staticmethod
    def fromkeys(iterable, value=None, /):
        ...

    def get(self, key, default=None, /):
        try:
            self._serializer.loads(self[key])
        except KeyError:
            return default

    def items(self):
        ...

    def keys(self):
        ...

    def pop(self, key, default=_default, /):
        try:
            value = self[key]
            del self[key]
            return value

        except KeyError:
            if default is _default:
                raise
            return default

    def popitem(self):
        ...

    def setdefault(self, key, default=None, /):
        pipeline = self._client.pipeline()
        pipeline.set(key, default, nx=True)
        pipeline.get(key)
        results = pipeline.execute()
        return self._serializer.loads(results[1])

    def update(self, mapping, **kwargs):
        mapping.update(kwargs)
        self._client.mset(mapping)

    def values(self):
        keys = self.keys()
        return self._client.mget(keys)


class redisdict_keys:

    def __iter__(self):
        ...

