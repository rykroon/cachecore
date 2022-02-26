from functools import cache
from math import ceil
from pathlib import Path
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


class Directory:

    def __init__(self, dir):
        self.path = Path(dir)
        if not self.path.is_absolute():
            self.path = self.path.absolute()

        if self.path.exists() and not self.path.is_dir():
            raise Exception

        if not self.path.exists():
            self.path.mkdir()

    def __getitem__(self, key):
        f = self.path / key
        try:
            return f.read_bytes()
        except FileNotFoundError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        f = self.path / key
        f.write_bytes(value)

    def __delitem__(self, key):
        f = self.path / key
        try:
            f.unlink()
        except FileNotFoundError:
            raise KeyError(key)

    def __contains__(self, key):
        f = self.path / key
        return f.exists()

    def __iter__(self):
        return self.path.iterdir()


def singleton(class_):
    class_.__new__ = cache(class_.__new__)
    return class_


