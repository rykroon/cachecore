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
MissingKey
```


## Complete API
```
- get(self, key: str) -> Union[Any, MissingKey]

- set(self, key: str, value: Any, ttl: Optional[int]=None)

- add(self, key: str, value: Any, ttl: Optional[int]=None) -> bool

- delete(self, key: str) -> bool

- has_key(self, key: str) -> bool

- get_many(self, keys: list[str]) -> list[Any]

- set_many(self, mapping: Iterable[tuple[str, Any]], ttl: Optional[int]=None)

- delete_many(self, keys: list[str]) -> list[bool]:

- get_ttl(self, key: str) -> Union[int, None, MissingKey]

- set_ttl(self, key: str, ttl: Optional[int]=None)

- incr(self, key, delta=1) -> int

- decr(self, key, delta=1) -> int

- clear(self)
```


## Cache Implementations
- Dummy
- Local Memory
- File System
- Memcached (Coming Soon)
- Redis
