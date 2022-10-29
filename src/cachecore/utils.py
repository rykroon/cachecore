from dataclasses import dataclass
from functools import cache
from math import ceil
import time
from typing import Optional, Any


def ttl_to_exptime(ttl: int | None) -> float | None:
    if ttl is None:
        return None
    return time.time() + ttl


def ttl_remaining(exp_time: float | None) -> int | None:
    if exp_time is None:
        return None
    return max(0, ceil(exp_time - time.time()))


def is_expired(exp_time: float | None) -> bool:
    return ttl_remaining(exp_time) == 0


@dataclass(slots=True)
class ExpiryValue:
    value: Any
    expires_at: Optional[float] = None

    @property
    def ttl(self):
        return ttl_remaining(self.expires_at)

    @ttl.setter
    def ttl(self, value):
        self.expires_at = ttl_to_exptime(value)

    def is_expired(self):
        return is_expired(self.expires_at)


class Singleton:
    @cache
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)


class KeepTTL(Singleton):
    ...


KEEP_TTL = KeepTTL()
