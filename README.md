# cachecore
A low-level caching library with multiple implementations.

Can be used as a stand-alone cacheing library or can be used to create higher level caching libraries.

## Basics
Get, set, delete, and check for the existence of a key using the following.

```
>>> import cachecore
>>> cache = cachecore.LocalCache()
>>> cache.set('a', 1)
>>> cache.get('a')
1
>>> cache.has_key('a')
True
>>> cache.delete('a')
True
>>> cache.has_key('a')
False
>>> cache.get('a')
None
```


## Complete API
```
    __getitem__(self, key: str) -> Any:

    __setitem__(self, key: str, value: Any):

    __delitem__(self, key: str):

    __contains__(self, key: str):

    __iter__(self):

    __len__(self):

    keys(self, pattern: str = None):

    get(self, key: str, default: Any = None) -> Any:

    set(self, key: str, value: Any, ttl: Optional[int] = None):

    add(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:

    replace(self, key: str, value: Any, ttl: Optional[int] = KEEP_TTL) -> bool:

    delete(self, key: str) -> bool:

    pop(self, key: str, default: Any = None):

    has_key(self, key: str) -> bool:

    get_many(self, keys: Iterable[str], default: Any = None) -> Iterable[Any]:

    set_many(self, mapping: Iterable[tuple[str, Any]], ttl: Optional[int] = None):

    delete_many(self, keys: Iterable[str]) -> Iterable[bool]:

    get_ttl(self, key: str, default: int = 0) -> Optional[int]:

    set_ttl(self, key: str, ttl: Optional[int] = None) -> bool:

    incr(self, key, delta=1) -> int:

    decr(self, key, delta=1) -> int:

    clear(self):
```


## Cache Implementations
- Dummy
- Local Memory
- File System
- Memcached (Coming Soon)
- Redis
