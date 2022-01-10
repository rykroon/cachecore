import unittest
import time

import redis

from cachecore.backends import BaseBackend
from cachecore.backends import DummyBackend
from cachecore.backends import LocalBackend
from cachecore.backends import RedisBackend
from cachecore.singletons import MissingKey


class TestBackend(unittest.TestCase):

    def test_all(self):
        backend = BaseBackend()
        with self.assertRaises(NotImplementedError):
            backend.get('a')

        with self.assertRaises(NotImplementedError):
            backend.set('a', b'1', None)

        with self.assertRaises(NotImplementedError):
            backend.delete('a')

        with self.assertRaises(NotImplementedError):
            backend.has_key('a')

        with self.assertRaises(NotImplementedError):
            backend.get_ttl('a')

        with self.assertRaises(NotImplementedError):
            backend.set_ttl('a', None)


class TestDummyBackend(unittest.TestCase):

    def setUp(self):
        self.backend = DummyBackend()

    def test_get(self):
        assert self.backend.get('a') is MissingKey
    
    def test_set(self):
        assert self.backend.set('a', 1, None) is None
        assert self.backend.get('a') is MissingKey

    def test_delete(self):
        assert self.backend.delete('a') == False
        self.backend.set('a', 1, None)
        assert self.backend.delete('a') == False

    def test_has_key(self):
        assert self.backend.has_key('a') == False
        self.backend.set('a', 1, None)
        assert self.backend.has_key('a') == False

    def test_get_many(self):
        assert self.backend.get_many('a', 'b', 'c') == [MissingKey] * 3

    def test_set_many(self):
        assert self.backend.set_many({'a': 1, 'b': 2, 'c': 3}, None) is None
        assert self.backend.get_many('a', 'b', 'c') == [MissingKey] * 3

    def test_delete_many(self):
        assert self.backend.delete_many('a', 'b', 'c') == [False, False, False]

    def test_get_ttl(self):
        assert self.backend.get_ttl('a') == 0
        self.backend.set('a', 1, None)
        assert self.backend.get_ttl('a') == 0
        self.backend.set_ttl('a', 300)
        assert self.backend.get_ttl('a') == 0


class AbstractBackendTest:

    def test_get_set(self):
        assert self.backend.get('a') is MissingKey

        self.backend.set('a', 1, None)
        assert self.backend.get('a') == 1
        assert self.backend.get_ttl('a') == None

        self.backend.set('a', 1, 20)
        assert self.backend.get_ttl('a') == 20
        assert self.backend.get('a') == 1

    def test_add(self):
        assert self.backend.add('a', 1, None) == True
        assert self.backend.add('a', 1, None) == False

        assert self.backend.add('b', 2, 300) == True
        assert self.backend.add('b', 2, 300) == False

    def test_delete(self):
        assert self.backend.delete('a') == False

        self.backend.set('a', 1, None)
        assert self.backend.delete('a') == True
        assert self.backend.get('a') is MissingKey
        
    def test_has_key(self):
        assert self.backend.has_key('a') == False
        self.backend.set('a', 1, None)
        assert self.backend.has_key('a') == True

    def test_get_set_ttl(self):
        assert self.backend.get_ttl('a') == 0

        self.backend.set('a', 1, None)
        assert self.backend.get_ttl('a') is None

        self.backend.set_ttl('a', 300)
        time.sleep(1)
        assert self.backend.get_ttl('a') == 299

    def test_get_set_many(self):
        assert self.backend.get_many('a', 'b', 'c') == [MissingKey] * 3

        self.backend.set_many({'a': 1, 'b': 2, 'c': 3}, None)
        assert self.backend.get_many('a', 'b', 'c') == [1, 2, 3]
        for k in ['a', 'b', 'c']:
            assert self.backend.get_ttl(k) is None

        self.backend.set_many({'a': 1, 'b': 2, 'c': 3}, 300)
        assert self.backend.get_many('a', 'b', 'c') == [1, 2, 3]
        for k in ['a', 'b', 'c']:
            assert self.backend.get_ttl(k) == 300

    def test_delete_many(self):
        self.backend.set_many({'a': 1, 'b': 2, 'c': 3}, None)
        assert self.backend.delete_many('a', 'b', 'c') == [True] * 3
        assert self.backend.get_many('a', 'b', 'c') == [MissingKey] * 3


class TestRedisBackend(unittest.TestCase, AbstractBackendTest):
    def setUp(self):
        client = redis.Redis()
        client.flushdb()
        self.backend = RedisBackend(client=client)


class TestLocalBackend(unittest.TestCase, AbstractBackendTest):
    def setUp(self):
        self.backend = LocalBackend()


if __name__ == '__main__':
    unittest.main()