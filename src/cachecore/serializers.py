import pickle
import json
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Serializer(Protocol):

    def dumps(self, obj: Any) -> bytes:
        ...

    def loads(self, data: bytes) -> Any:
        ...


class JSONSerializer:

    def __init__(self, encoder=None, decoder=None):
        self.encoder = encoder
        self.decoder = decoder

    def dumps(self, obj: Any) -> bytes:
        json_string = json.dumps(
            obj,
            cls=self.encoder,
            separators=(',', ':')
        )
        return json_string.encode()

    def loads(self, data: bytes) -> Any:
        return json.loads(data, cls=self.decoder)


class RedisSerializer:

    def dumps(self, obj: Any) -> bytes:
        if type(obj) == int:
            return str(obj).encode()
        return pickle.dumps(obj)

    def loads(self, data: bytes) -> Any:
        try:
            return int(data)
        except ValueError:
            return pickle.loads(data)
