    
_default = object()

    
class BaseDict(dict):
    
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