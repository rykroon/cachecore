from functools import cache
from math import ceil
import time


def ttl_to_exptime(ttl):
    if ttl is None:
        return None
    return time.time() + ttl


def ttl_remaining(exp_time):
    if exp_time is None:
        return None
    return max(0, ceil(exp_time - time.time()))


def is_expired(exp_time):
    return ttl_remaining(exp_time) == 0


class Singleton:
    ...


Singleton.__new__ = cache(Singleton.__new__)


class KeepTTL(Singleton):
    ...


KEEP_TTL = KeepTTL()
