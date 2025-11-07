from typing import Any, Iterable, Mapping

from .utils import ExpiryValue, _missing_key


class LocalCache:

    def __init__(self):
        self._data: dict[str, ExpiryValue] = {}

    def _get(self, key: str) -> ExpiryValue | object:
        ev = self._data.get(key)
        if ev is None:
            return _missing_key

        if ev.is_expired():
            del self._data[key]
            return _missing_key

        return ev

    def get(self, key: str, default=None):
        ev = self._get(key)
        if ev is _missing_key:
            return default
        return ev.value

    def set(self, key: str, value: Any, ttl: int | None = None):
        self._data[key] = ExpiryValue(value, ttl)

    def delete(self, key: str) -> bool:
        ev = self._get(key)
        if ev is _missing_key:
            return False

        del self._data[key]
        return False if ev.is_expired() else True

    def has_key(self, key: str) -> bool:
        return self._get(key) is not _missing_key

    def __contains__(self, key: str) -> bool:
        return self.has_key(key)

    def add(self, key: str, value: Any, ttl: int | None = None) -> bool:
        if key not in self._data:
            self.set(key, value, ttl)
            return True
        return False

    def touch(self, key: str, ttl: int | None = None) -> bool:
        ev = self._get(key)
        if ev is _missing_key or ev.is_expired():
            return False
 
        ev.ttl = ttl
        return True

    def get_or_set(self, key: str, default: Any, ttl: int | None = None) -> Any:
        ev = self._get(key)
        if ev is _missing_key:
            self.set(key, default, ttl)
            return default
        return ev.value

    def get_many(self, keys: Iterable[str]) -> dict[str, Any]:
        return {
            k: ev.value
            for k, ev in self._data.items()
            if k in keys and not ev.is_expired()
        }

    def set_many(self, data: Mapping, ttl: int | None = None) -> list[str]:
        values = {k: ExpiryValue(v, ttl) for k, v in data.items()}
        self._data.update(values)
        return []

    def delete_many(self, keys: Iterable[str]):
        for key in keys:
            self.delete(key)

    def incr(self, key: str, delta: int = 1) -> int:
        ev = self._get(key)
        if ev is _missing_key:
            raise ValueError("key not found")

        ev.value += delta
        return ev.value
    
    def decr(self, key: str, delta: int = 1) -> int:
        return self.incr(key, -delta)

    def clear(self) -> None:
        self._data.clear()
