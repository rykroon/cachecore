from base64 import b32encode, b32decode
from pathlib import Path
import pickle
from struct import pack, unpack

from .base import BaseCache
from ..utils import ttl_to_exptime, ttl_remaining, is_expired, KEEP_TTL


class FileCache(BaseCache):

    serializer = pickle

    def __init__(self, dir, ext='.cachecore'):
        self._dir = Path(dir)
        if not self._dir.is_absolute():
            self._dir = self._dir.resolve()

        if self._dir.exists() and not self._dir.is_dir():
            raise Exception

        self._mkdir()
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

    def __iter__(self):
        for path in self._iterdir():
            fname = path.name.rstrip(self._ext)
            yield b32decode(fname).decode()

    def __len__(self):
        return len(list(self._iterdir()))

    def _mkdir(self):
        if not self._dir.exists():
            self._dir.mkdir()

    def _iterdir(self):
        for path in self._dir.iterdir():
            if not path.is_file():
                continue

            if not path.name.endswith(self._ext):
                continue

            yield path

    def _key_to_path(self, key):
        fname = b32encode(key.encode()).decode()
        fname += self._ext
        return self._dir / fname

    def _read(self, path, incval=False):
        if not path.exists():
            return False, None, None

        with path.open('rb') as f:
            expires_at = unpack('d', f.read(8))[0]
            if expires_at == 0.0:
                expires_at = None

            if is_expired(expires_at):
                f.close()
                path.unlink(missing_ok=True)
                return False, None, None

            if not incval:
                return True, expires_at, None

            value = self.serializer.loads(f.read())
            return True, expires_at, value

    def _write(self, path, value, expires_at):
        with path.open('wb') as f:
            if expires_at is None:
                expires_at = 0.0

            f.write(pack('d', expires_at))
            f.write(self.serializer.dumps(value))

    def set(self, key, value, ttl=None):
        path = self._key_to_path(key)
        expires_at = ttl_to_exptime(ttl)
        self._write(path, value, expires_at)

    def replace(self, key, value, ttl=KEEP_TTL):
        path = self._key_to_path(key)
        exists, expires_at, _ = self._read(path)
        if not exists:
            return False

        if ttl is not KEEP_TTL:
            expires_at = ttl_to_exptime(ttl)

        self._write(path, value, expires_at)
        return True

    def get_ttl(self, key, default=0):
        path = self._key_to_path(key)
        exists, expires_at, _ = self._read(path)
        if not exists:
            return default
        return ttl_remaining(expires_at)

    def set_ttl(self, key, ttl=None):
        path = self._key_to_path(key)
        exists, _, value = self._read(path, incval=True)
        if not exists:
            return False
        expires_at = ttl_to_exptime(ttl)
        self._write(path, value, expires_at)
        return True

    def incr(self, key, delta=1):
        path = self._key_to_path(key)
        exists, expires_at, value = self._read(path, incval=True)

        if not exists:
            value = 0
            expires_at = None

        value += delta
        self._write(path, value, expires_at)
        return value

    def clear(self):
        for path in self._iterdir():
            path.unlink(missing_ok=True)
