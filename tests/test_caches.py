import os
import unittest
import time

import redis

from pycachecore.caches import CacheInterface
from pycachecore.caches import DummyCache
from pycachecore.caches import LocalCache
from pycachecore.caches import RedisCache
from pycachecore.caches import FileCache
from pycachecore.utils import MISSING_KEY


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
        assert self.cache.get('a') is MISSING_KEY
    
    def test_set(self):
        assert self.cache.set('a', 1, None) is None
        assert self.cache.get('a') is MISSING_KEY

    def test_delete(self):
        assert self.cache.delete('a') == False
        self.cache.set('a', 1, None)
        assert self.cache.delete('a') == False

    def test_has_key(self):
        assert self.cache.has_key('a') == False
        self.cache.set('a', 1, None)
        assert self.cache.has_key('a') == False

    def test_get_many(self):
        assert self.cache.get_many('a', 'b', 'c') == [MISSING_KEY] * 3

    def test_set_many(self):
        assert self.cache.set_many({'a': 1, 'b': 2, 'c': 3}.items(), None) is None
        assert self.cache.get_many('a', 'b', 'c') == [MISSING_KEY] * 3

    def test_delete_many(self):
        assert self.cache.delete_many('a', 'b', 'c') == [False, False, False]

    def test_get_ttl(self):
        assert self.cache.get_ttl('a') == MISSING_KEY
        self.cache.set('a', 1)
        assert self.cache.get_ttl('a') == MISSING_KEY
        self.cache.set_ttl('a', 300)
        assert self.cache.get_ttl('a') == MISSING_KEY


class AbstractCacheTest:

    def test_get_set(self):
        assert self.cache.get('a') is MISSING_KEY

        self.cache.set('a', 1)
        assert self.cache.get('a') == 1
        assert self.cache.get_ttl('a') == None

        self.cache.set('a', 1, 20)
        assert self.cache.get_ttl('a') == 20
        assert self.cache.get('a') == 1

    def test_add(self):
        assert self.cache.add('a', 1) == True
        assert self.cache.add('a', 1) == False

        assert self.cache.add('b', 2, 300) == True
        assert self.cache.add('b', 2, 300) == False

    def test_delete(self):
        assert self.cache.delete('a') == False

        self.cache.set('a', 1)
        assert self.cache.delete('a') == True
        assert self.cache.get('a') is MISSING_KEY
        
    def test_has_key(self):
        assert self.cache.has_key('a') == False
        self.cache.set('a', 1)
        assert self.cache.has_key('a') == True
        self.cache.set('a', 1, 1)
        time.sleep(1)
        assert self.cache.has_key('a') == False

    def test_get_set_ttl(self):
        assert self.cache.get_ttl('a') is MISSING_KEY

        self.cache.set('a', 1)
        assert self.cache.get_ttl('a') is None

        self.cache.set_ttl('a', 300)
        time.sleep(1)
        assert self.cache.get_ttl('a') == 299

    def test_get_set_many(self):
        assert self.cache.get_many('a', 'b', 'c') == [MISSING_KEY] * 3

        self.cache.set_many([('a', 1), ('b', 2), ('c', 3)])
        assert self.cache.get_many('a', 'b', 'c') == [1, 2, 3]
        for k in ['a', 'b', 'c']:
            assert self.cache.get_ttl(k) is None

        self.cache.set_many({'a': 1, 'b': 2, 'c': 3}.items(), 300)
        assert self.cache.get_many('a', 'b', 'c') == [1, 2, 3]
        for k in ['a', 'b', 'c']:
            assert self.cache.get_ttl(k) == 300

    def test_delete_many(self):
        self.cache.set_many({'a': 1, 'b': 2, 'c': 3}.items())
        assert self.cache.delete_many('a', 'b', 'c') == [True] * 3
        assert self.cache.get_many('a', 'b', 'c') == [MISSING_KEY] * 3

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