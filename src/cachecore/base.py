from fnmatch import fnmatch
import typing as t


class BaseCache:

    def __len__(self) -> int:
        return len(list(self))

    def keys(self, pattern: str | None = None) -> t.Iterator[str]:
        for key in self:
            if pattern is not None:
                if not fnmatch(key, pattern):
                    continue
            yield key

    def get(self, key: str, default: t.Any = None) -> t.Any:
        try:
            return self[key]
        except KeyError:
            return default

    def add(self, key: str, value: t.Any, ttl: int | None = None) -> bool:
        if self.exists(key):
            return False
        self.set(key, value, ttl)
        return True

    def delete(self, key: str) -> bool:
        try:
            del self[key]
        except KeyError:
            return False
        return True

    def pop(self, key: str, default: t.Any | None = None) -> t.Any:
        value = self.get(key, default)
        self.delete(key)
        return value

    def exists(self, key: str) -> bool:
        return key in self

    def get_many(self, keys: list[str], default: t.Any=None) -> t.Iterable[t.Any]:
        return (self.get(k, default) for k in keys)

    def set_many(self, mapping: t.Mapping[str, t.Any], ttl: int | None = None) -> None:
        for k, v in mapping:
            self.set(k, v, ttl)

    def delete_many(self, keys: list[str]) -> t.Iterable[bool]:
        return (self.delete(k) for k in keys)

    def decr(self, key: str, delta: int = 1) -> int:
        return self.incr(key, -delta)
