from hashlib import md5
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

    def _read(self, path, exclude_value=False):
        if not path.exists():
            return MISSING_KEY, MISSING_KEY

        with path.open('rb') as f:
            line1 = f.readline()
            line1 = line1.rstrip(b'\n')
            expires_at = float(line1) if line1 else None
            if is_expired(expires_at):
                # delete file
                return MISSING_KEY, MISSING_KEY

            ttl = ttl_remaining(expires_at)
            if exclude_value:
                return MISSING_KEY, ttl
            
            line2 = f.readline()
            line2 = line2.rstrip(b'\n')
            value = self.serializer.loads(line2)
            return value, ttl

    def _write(self, path, value, ttl):
        value = self.serializer.dumps(value)
        exptime = ttl_to_exptime(ttl)
        exptime = str(exptime).encode() if exptime else b''
        data = exptime + b'\n' + value + b'\n'
        path.write_bytes(data)

    def get(self, key):
        path = self._key_to_path(key)
        value, _ = self._read(path)
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
        _, ttl = self._read(path, exclude_value=True)
        return ttl is not MISSING_KEY

    def get_many(self, *keys):
        return [self.get(k) for k in keys]

    def set_many(self, mapping, ttl=None):
        for k, v in mapping:
            self.set(k, v, ttl)

    def delete_many(self, *keys):
        return [self.delete(k) for k in keys]

    def get_ttl(self, key):
        path = self._key_to_path(key)
        _, ttl = self._read(path, exclude_value=True)
        return ttl

    def set_ttl(self, key, ttl=None):
        path = self._key_to_path(key)
        value, _ = self._read(path)
        if value is not MISSING_KEY:
            self._write(path, value, ttl)

    def incr(self, key, delta=1):
        path = self._key_to_path(key)
        value, ttl = self._read(path)

        if value is MISSING_KEY:
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
