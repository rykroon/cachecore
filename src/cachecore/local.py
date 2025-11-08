from typing import Any, Iterable, Mapping

from .utils import ExpiryDict


class DictCache:

    def __init__(self):
        self._data: ExpiryDict = ExpiryDict()

    def get(self, key: str, default=None):
        item =  self._data.get(key)
        return default if item is None else item.value

    def set(self, key: str, value: Any, ttl: int | None = None):
        self._data.set(key, value, ttl)

    def delete(self, *keys: str) -> int:
        return sum(self._data.pop(k, None) is not None for k in keys)

    def exists(self, *keys: str) -> int:
        return sum(k in self for k in keys)

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def add(self, key: str, value: Any, ttl: int | None = None) -> bool:
        if key not in self:
            self.set(key, value, ttl)
            return True
        return False

    def replace(self, key: str, value: Any, ttl: int | None = None, keepttl: bool = False):
        if ttl and bool:
            raise ValueError("ttl and keepttl are emutually exclusive")

        item = self._data.get(key)
        if item is None:
            return False
        
        item.value = value
        if ttl is not None:
            item.ttl = ttl
        
        return True

    def ttl(self, key: str) -> int:
        item = self._data.get(key)
        return None if item is None else item.ttl
    
    def expire(self, key: str, ttl: int) -> bool:
        item = self._data.get(key)
        if item is None:
            return False

        item.ttl = ttl
        return True
    
    def persist(self, key: str):
        pass

    def get_many(self, keys: Iterable[str], default=None) -> list[Any]:
        return [self.get(k, default) for k in keys]

    def set_many(self, data: Mapping, ttl: int | None = None):
        for k, v in data.items():
            self.set(k, v, ttl)

    def incr(self, key: str, amount: int = 1) -> int:
        value = self.get(key, 0) + amount
        self.set(key, value)
        return value

    def decr(self, key: str, amount: int = 1) -> int:
        return self.incr(key, -amount)

    def clear(self) -> None:
        self._data.clear()
