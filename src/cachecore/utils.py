from functools import cache
from math import ceil
import time
from typing import Optional


def ttl_to_exptime(ttl: Optional[int]) -> float:
    if ttl is None:
        return None
    return time.time() + ttl


def ttl_remaining(exp_time: Optional[float]) -> int:
    if exp_time is None:
        return None
    return max(0, ceil(exp_time - time.time()))


def is_expired(exp_time: Optional[float]) -> bool:
    return ttl_remaining(exp_time) == 0


class Singleton:
    @cache
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)


class KeepTTL(Singleton):
    ...


KEEP_TTL = KeepTTL()
