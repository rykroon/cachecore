import os


_default = object()


class FileDict(dict):
    
    def __init__(self, dir):
        self._dir = os.path.abspath(dir)
        self._createdir()

    def __getitem__(self, key):
        ...

    def __setitem__(self, key, value):
        ...

    def __delitem__(self, key):
        ...

    def __contains__(self, key):
        ...

    def _createdir(self):
        # Set the umask because os.makedirs() doesn't apply the "mode" argument
        # to intermediate-level directories.
        old_umask = os.umask(0o077)
        try:
            os.makedirs(self._dir, 0o700, exist_ok=True)
        finally:
            os.umask(old_umask)

    def clear(self):
        ...

    def copy(self):
        ...

    @staticmethod
    def fromkeys(self, iterable, value=None, /):
        ...

    def get(self, key, default=None, /):
        ...

    def items(self):
        ...

    def keys(self):
        ...

    def pop(self, key, default=_default, /):
         ...

    def popitem(self):
        ...

    def setdefault(self, key, default=None, /):
        ...

    def update(self, mapping, **kwargs):
        ...

    def values(self):
        ...

        