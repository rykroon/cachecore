from functools import cache
from math import ceil
from pathlib import Path
import time


class Value:

    """
        A helper class for storing values with a TTL.
    """

    def __init__(self, value, expires_at=None):
        self.value = value
        self.expires_at = expires_at

    @property
    def ttl(self):
        if self.expires_at is None:
            return None

        return max(0, ceil(self.expires_at - time.time()))

    @ttl.setter
    def ttl(self, ttl):
        self.expires_at = None if ttl is None else time.time() + ttl

    def is_expired(self):
        return self.ttl == 0


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


@singleton
class MissingKey:

    def __bool__(self):
        return False

    def __repr__(self):
        return 'MissingKey'


MISSING_KEY = MissingKey()
