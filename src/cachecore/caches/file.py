from hashlib import md5
from pathlib import Path
import pickle

from cachecore.caches import BaseCache
from cachecore.utils import ttl_to_exptime, ttl_remaining, is_expired


class FileCache(BaseCache):

    serializer = pickle

    def __init__(self, dir, ext='.cachecore'):
        self._dir = Path(dir)
        if not self._dir.is_absolute():
            self._dir = self._dir.resolve()

        if self._dir.exists() and not self._dir.is_dir():
            raise Exception

        self._createdir()
        self._ext = ext

    def __getitem__(self, key):
        path = self._key_to_path(key)
        exists, _, value = self._read(path, incval=True)
        if not exists:
            raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        path = self._key_to_path(key)
        self._write(path, value, None)

    def __delitem__(self, key):
        if not self.has_key(key):
            raise KeyError(key)

        path = self._key_to_path(key)
        try:
            path.unlink()
        except FileNotFoundError:
            raise KeyError(key)

    def __contains__(self, key):
        path = self._key_to_path(key)
        exists, _, _ = self._read(path)
        return exists

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

    def set(self, key, value, ttl=None):
        path = self._key_to_path(key)
        self._write(path, value, ttl)

    def get_ttl(self, key, default=0):
        path = self._key_to_path(key)
        exists, ttl, _ = self._read(path, incttl=True)
        if not exists:
            return default
        return ttl

    def set_ttl(self, key, ttl=None):
        path = self._key_to_path(key)
        exists, _, value = self._read(path, incval=True)
        if not exists:
            return False
        self._write(path, value, ttl)
        return True

    def incr(self, key, delta=1):
        path = self._key_to_path(key)
        exists, ttl, value = self._read(path, incval=True)

        if not exists:
            value = 0
            ttl = None

        value += delta
        self._write(path, value, ttl)
        return value

    def clear(self):
        for path in self._dir.iterdir():
            if not path.is_file():
                continue

            if not path.name.endswith(self._ext):
                continue

            path.unlink(missing_ok=True)
