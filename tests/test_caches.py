import os
import string
import time
import unittest


import redis

from src.cachecore.caches import CacheInterface
from src.cachecore.caches import DummyCache
from src.cachecore.caches import LocalCache
from src.cachecore.caches import RedisCache
from src.cachecore.caches import FileCache


class TestProtocol(unittest.TestCase):
    def test_protocol(self):
        assert issubclass(DummyCache, CacheInterface)
        assert issubclass(LocalCache, CacheInterface)
        assert issubclass(RedisCache, CacheInterface)
        assert issubclass(FileCache, CacheInterface)


class TestDummyCache(unittest.TestCase):

    def setUp(self):
        self.cache = DummyCache()

    def test_getitem(self):
        with self.assertRaises(KeyError):
            self.cache['a']

    def test_setitem(self):
        self.cache['a'] = 1
        with self.assertRaises(KeyError):
            self.cache['a']

    def test_delitem(self):
        with self.assertRaises(KeyError):
            del self.cache['a']

        self.cache['a'] = 1

        with self.assertRaises(KeyError):
            del self.cache['a']

    def test_get(self):
        assert self.cache.get('a') is None

    def test_set(self):
        assert self.cache.set('a', 1, None) is None
        assert self.cache.get('a') is None

    def test_add_replace(self):
        assert self.cache.add('a', 1) is True
        assert self.cache.replace('a', 1) is False

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

    def test_incr_decr(self):
        assert self.cache.incr('a') == 1
        assert self.cache.incr('a', 20) == 20
        assert self.cache.decr('a') == -1
        assert self.cache.decr('a', 20) == -20


class AbstractCacheTest:

    def test_getsetitem(self):
        with self.assertRaises(KeyError):
            self.cache['a']

        self.cache['a'] = 1

        assert self.cache['a'] == 1

    def test_delitem(self):
        with self.assertRaises(KeyError):
            del self.cache['a']

        self.cache['a'] = 1
        del self.cache['a']

    def test_iter(self):
        letters = [char for char in string.ascii_letters]
        data = dict.fromkeys(letters)
        self.cache.set_many(data.items())

        for key in self.cache:
            assert key in letters

    def test_keys(self):
        pattern = 'h*llo'
        self.cache.set_many(
            (
                ('hello', None),
                ('hallo', None),
                ('HELLO', None),
                ('world', None)
            )
        )
        for key in self.cache.keys(pattern):
            assert key in ('hello', 'hallo', 'HELLO')

    def test_get_set(self):
        assert self.cache.get('a') is None
        assert self.cache.get('a', default=1) == 1

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

    def test_replace(self):
        assert self.cache.replace('a', 1) is False
        assert not self.cache.has_key('a')

        self.cache.set('a', 1, 300)

        # replace and keep ttl
        assert self.cache.replace('a', 2) is True
        assert self.cache.get_ttl('a', 300)
        assert self.cache.get('a') == 2

        # replace and update ttl
        assert self.cache.replace('a', 3, None) is True
        assert self.cache.get_ttl('a') is None
        assert self.cache.get('a') is 3

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

    def test_pop(self):
        assert self.cache.pop('a') is None
        self.cache.set('a', 1)
        assert self.cache.pop('a') == 1
        assert not self.cache.has_key('a')

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

    def test_incr(self):
        assert self.cache.incr('a') == 1
        assert self.cache.incr('a') == 2
        assert self.cache.incr('b', 10) == 10
        assert self.cache.incr('b', 10) == 20

    def test_decr(self):
        assert self.cache.decr('a') == -1
        assert self.cache.decr('a') == -2
        assert self.cache.decr('b', 10) == -10
        assert self.cache.decr('b', 10) == -20

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
