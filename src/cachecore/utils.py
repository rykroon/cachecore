from dataclasses import dataclass, field, InitVar
from functools import cache
from math import ceil
import time
from typing import Any


_missing_key = object()


@dataclass(slots=True)
class ExpiryValue:
    value: Any
    ttl: InitVar[int | None]
    expires_at: float = field(init=False)

    def __post_init__(self, ttl: int | None):
        self.set_ttl(ttl)

    @property
    def ttl(self) -> int | None:
        if self.expires_at == float("inf"):
            return None
        return max(0, ceil(self.expires_at - time.time()))

    def set_ttl(self, ttl: int | None):
        expiry = float("inf") if ttl is None else ttl
        self.expires_at = time.time() + expiry

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class Singleton:
    @cache
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)


class KeepTTL(Singleton):
    ...


KEEP_TTL = KeepTTL()
