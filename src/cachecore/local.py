from typing import Any, Iterable, Mapping

from .utils import ExpiryValue, ExpiryDict, _missing_key


class DictCache:

    def __init__(self):
        self._data: ExpiryDict = ExpiryDict()

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value: Any, ttl: int | None = None):
        self._data.set(key, value, ttl)

    def delete(self, *keys: str) -> int:
        return sum(self._data.pop(k, _missing_key) is not _missing_key for k in keys)

    def exists(self, *keys: str) -> int:
        return sum(k in self._data for k in keys)

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def add(self, key: str, value: Any, ttl: int | None = None) -> bool:
        if key not in self:
            self.set(key, value, ttl)
            return True
        return False

    def replace(self, key: str, value: Any):
        pass

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

    def incr(self, key: str, delta: int = 1) -> int:
        pass

    def decr(self, key: str, delta: int = 1) -> int:
        return self.incr(key, -delta)

    def clear(self) -> None:
        self._data.clear()
