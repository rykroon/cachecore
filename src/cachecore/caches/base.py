from fnmatch import fnmatch


class BaseCache:

    def __len__(self):
        return len(list(self))

    def keys(self, pattern=None):
        for key in self:
            if pattern is not None:
                if not fnmatch(key, pattern):
                    continue
            yield key

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def add(self, key, value, ttl=None):
        if self.exists(key):
            return False
        self.set(key, value, ttl)
        return True

    def delete(self, key):
        try:
            del self[key]
        except KeyError:
            return False
        return True

    def pop(self, key, default=None):
        value = self.get(key, default)
        self.delete(key)
        return value

    def exists(self, key):
        return key in self

    def get_many(self, keys, default=None):
        return (self.get(k, default) for k in keys)

    def set_many(self, mapping, ttl=None):
        for k, v in mapping:
            self.set(k, v, ttl)

    def delete_many(self, keys):
        return (self.delete(k) for k in keys)

    def decr(self, key, delta=1):
        return self.incr(key, -delta)
