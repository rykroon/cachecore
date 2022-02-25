from hashlib import md5
from math import exp
from pathlib import Path
import pickle

from cachecore.utils import MISSING_KEY, ttl_to_exptime, ttl_remaining, \
    is_expired


class FileCache:

    serializer = pickle

    def __init__(self, dir, ext='.cachecore'):
        self._dir = Path(dir)
        if not self._dir.is_absolute():
            self._dir = self._dir.resolve()

        if self._dir.exists() and not self._dir.is_dir():
            raise Exception

        self._createdir()
        self._ext = ext

    def _createdir(self):
        if not self._dir.exists():
            self._dir.mkdir()

    def _key_to_path(self, key):
        fname = md5(key.encode(), usedforsecurity=False).hexdigest()
        fname += self._ext
        return self._dir / fname

    def _read(self, path, incttl=False, incval=False):
        # if include value is True, then include expiration time must be True
        if incval:
            incttl = True

        if not path.exists():
            return False, None, None

        with path.open('rb') as f:
            line1 = f.readline()
            line1 = line1.rstrip(b'\n')
            expires_at = float(line1) if line1 else None
            if is_expired(expires_at):
                f.close()
                path.unlink(missing_ok=True)
                return False, None, None

            if not incttl:
                return True, None, None

            ttl = ttl_remaining(expires_at)

            if not incval:
                return True, ttl, None
            
            line2 = f.readline()
            line2 = line2.rstrip(b'\n')
            value = self.serializer.loads(line2)
            return True, ttl, value

    def _write(self, path, value, ttl):
        value = self.serializer.dumps(value)
        exptime = ttl_to_exptime(ttl)
        exptime = str(exptime).encode() if exptime else b''
        data = exptime + b'\n' + value + b'\n'
        path.write_bytes(data)

    def get(self, key):
        path = self._key_to_path(key)
        exists, _, value = self._read(path, incval=True)
        if not exists:
            return MISSING_KEY
        return value

    def set(self, key, value, ttl=None):
        path = self._key_to_path(key)
        self._write(path, value, ttl)

    def add(self, key, value, ttl=None):
        if self.has_key(key):
            return False
        self.set(key, value, ttl)
        return True

    def delete(self, key):
        if not self.has_key(key):
            return False
        path = self._key_to_path(key)
        try:
            path.unlink()
        except FileNotFoundError:
            return False
        return True

    def has_key(self, key):
        path = self._key_to_path(key)
        exists, _, _ = self._read(path)
        return exists

    def get_many(self, *keys):
        return [self.get(k) for k in keys]

    def set_many(self, mapping, ttl=None):
        for k, v in mapping:
            self.set(k, v, ttl)

    def delete_many(self, *keys):
        return [self.delete(k) for k in keys]

    def get_ttl(self, key):
        path = self._key_to_path(key)
        exists, ttl, _ = self._read(path, incttl=True)
        if not exists:
            return MISSING_KEY
        return ttl

    def set_ttl(self, key, ttl=None):
        path = self._key_to_path(key)
        exists, _, value = self._read(path, incval=True)
        if exists:
            self._write(path, value, ttl)

    def incr(self, key, delta=1):
        path = self._key_to_path(key)
        exists, ttl, value = self._read(path, incval=True)

        if not exists:
            value = 0
            ttl = None

        value += delta
        self._write(path, value, ttl)
        return value

    def decr(self, key, delta=1):
        return self.incr(key, -delta)

    def clear(self):
        for path in self._dir.iterdir():
            if not path.is_file():
                continue

            if not path.name.endswith(self._ext):
                continue

            path.unlink(missing_ok=True)
