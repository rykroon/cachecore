import os
import unittest
import time

import redis

from cachecore.caches import CacheInterface
from cachecore.caches import DummyCache
from cachecore.caches import LocalCache
from cachecore.caches import RedisCache
from cachecore.caches import FileCache
from cachecore.utils import MISSING_KEY


class TestProtocol(unittest.TestCase):
    def test_protocol(self):
        assert issubclass(DummyCache, CacheInterface)
        assert issubclass(LocalCache, CacheInterface)
        assert issubclass(RedisCache, CacheInterface)
        assert issubclass(FileCache, CacheInterface)


class TestDummyCache(unittest.TestCase):

    def setUp(self):
        self.cache = DummyCache()

    def test_get(self):
        assert self.cache.get('a') is None

    def test_set(self):
        assert self.cache.set('a', 1, None) is None
        assert self.cache.get('a') is None

    def test_delete(self):
        assert self.cache.delete('a') is False
        self.cache.set('a', 1, None)
        assert self.cache.delete('a') is False

    def test_has_key(self):
        assert self.cache.has_key('a') is False
        self.cache.set('a', 1, None)
        assert self.cache.has_key('a') is False

    def test_get_many(self):
        assert self.cache.get_many(['a', 'b', 'c']) == [None] * 3

    def test_set_many(self):
        mapping = {'a': 1, 'b': 2, 'c': 3}.items()
        assert self.cache.set_many(mapping, None) is None
        assert self.cache.get_many(['a', 'b', 'c']) == [None] * 3

    def test_delete_many(self):
        assert self.cache.delete_many(['a', 'b', 'c']) == [False, False, False]

    def test_get_ttl(self):
        assert self.cache.get_ttl('a') == 0
        assert self.cache.get_ttl('a', -1) == -1
        self.cache.set('a', 1)
        assert self.cache.get_ttl('a') == 0
        assert self.cache.set_ttl('a', 300) is False
        assert self.cache.get_ttl('a') == 0


class AbstractCacheTest:

    def test_get_set(self):
        assert self.cache.get('a') is None
        assert self.cache.get('a', default=MISSING_KEY) is MISSING_KEY

        self.cache.set('a', 1)
        assert self.cache.get('a') == 1
        assert self.cache.get_ttl('a') is None

        self.cache.set('a', 1, 20)
        assert self.cache.get_ttl('a') == 20
        assert self.cache.get('a') == 1

    def test_add(self):
        assert self.cache.add('a', 1) is True
        assert self.cache.add('a', 1) is False

        assert self.cache.add('b', 2, 300) is True
        assert self.cache.add('b', 2, 300) is False

    def test_delete(self):
        assert self.cache.delete('a') is False

        self.cache.set('a', 1)
        assert self.cache.delete('a') is True
        assert self.cache.get('a') is None

        # Check so that if a key expires then deleting
        # should return False.
        self.cache.set('a', 1, 1)
        time.sleep(1)
        assert self.cache.delete('a') is False

    def test_has_key(self):
        assert self.cache.has_key('a') is False
        self.cache.set('a', 1)
        assert self.cache.has_key('a') is True
        self.cache.set('a', 1, 1)
        time.sleep(1)
        assert self.cache.has_key('a') is False

    def test_get_set_ttl(self):
        assert self.cache.get_ttl('a') == 0
        assert self.cache.get_ttl('a', -1) == -1

        self.cache.set('a', 1)
        assert self.cache.get_ttl('a') is None

        assert self.cache.set_ttl('a', 300) is True
        time.sleep(1)
        assert self.cache.get_ttl('a') == 299

        assert self.cache.set_ttl('b', 300) is False

    def test_get_set_many(self):
        assert self.cache.get_many(['a', 'b', 'c']) == [None] * 3

        self.cache.set_many([('a', 1), ('b', 2), ('c', 3)])
        assert self.cache.get_many(['a', 'b', 'c']) == [1, 2, 3]
        for k in ['a', 'b', 'c']:
            assert self.cache.get_ttl(k) is None

        self.cache.set_many({'a': 1, 'b': 2, 'c': 3}.items(), 300)
        assert self.cache.get_many(['a', 'b', 'c']) == [1, 2, 3]
        for k in ['a', 'b', 'c']:
            assert self.cache.get_ttl(k) == 300

    def test_delete_many(self):
        self.cache.set_many({'a': 1, 'b': 2, 'c': 3}.items())
        assert self.cache.delete_many(['a', 'b', 'c']) == [True] * 3
        assert self.cache.get_many(['a', 'b', 'c']) == [None] * 3

    def test_incr_decr(self):
        assert self.cache.incr('a') == 1
        assert self.cache.incr('b', 20) == 20

        assert self.cache.decr('a') == 0
        assert self.cache.decr('b', 5) == 15

    def test_clear(self):
        self.cache.set_many([('a', 1), ('b', 2), ('c', 3)])
        self.cache.clear()
        for k in ('a', 'b', 'c'):
            assert self.cache.has_key(k) is False


class TestLocalCache(unittest.TestCase, AbstractCacheTest):
    def setUp(self):
        self.cache = LocalCache()


class TestFileCache(unittest.TestCase, AbstractCacheTest):
    def setUp(self):
        home_dir = os.environ['HOME']
        dir = os.path.join(home_dir, 'cachecore-tests')
        self.cache = FileCache(dir=dir)

        for fname in os.listdir(dir):
            if fname.endswith('.cachecore'):
                fpath = os.path.join(dir, fname)
                os.remove(fpath)


class TestRedisCache(unittest.TestCase, AbstractCacheTest):
    def setUp(self):
        client = redis.Redis()
        client.flushdb()
        self.cache = RedisCache(client=client)


if __name__ == '__main__':
    unittest.main()
