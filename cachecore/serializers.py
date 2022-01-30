import pickle
from typing import Protocol, runtime_checkable


@runtime_checkable
class Serializer(Protocol):

    def dumps(self, obj):
        ...

    def loads(self, data):
        ...


class RedisSerializer:

    def dumps(self, value):
        if type(value) == int:
            return value
        return pickle.dumps(value)

    def loads(self, value):
        try:
            return int(value)
        except ValueError:
            return pickle.loads(value)
