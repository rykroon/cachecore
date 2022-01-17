import pickle
from typing import Protocol, runtime_checkable


@runtime_checkable
class StringSerializer(Protocol):

    def dumps(self, obj):
        ...

    def loads(self, data):
        ...


@runtime_checkable
class FileSerializer(Protocol):

    def dump(self, obj, file):
        ...

    def load(self, file):
        ...


@runtime_checkable
class Serializer(StringSerializer, FileSerializer, Protocol):
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
