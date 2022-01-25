import os
import unittest
import time

import redis

from cachecore.backends import BackendProtocol
from cachecore.backends import DummyBackend
from cachecore.backends import LocalBackend
from cachecore.backends import RedisBackend
from cachecore.backends import FileBackend
from cachecore.utils import MISSING_KEY


class TestProtocol(unittest.TestCase):
    def test_protocol(self):
        assert issubclass(DummyBackend, BackendProtocol)
        assert issubclass(LocalBackend, BackendProtocol)
        assert issubclass(RedisBackend, BackendProtocol)
        assert issubclass(FileBackend, BackendProtocol)


class TestDummyBackend(unittest.TestCase):

    def setUp(self):
        self.backend = DummyBackend()

    def test_get(self):
        assert self.backend.get('a') is MISSING_KEY
    
    def test_set(self):
        assert self.backend.set('a', 1, None) is None
        assert self.backend.get('a') is MISSING_KEY

    def test_delete(self):
        assert self.backend.delete('a') == False
        self.backend.set('a', 1, None)
        assert self.backend.delete('a') == False

    def test_has_key(self):
        assert self.backend.has_key('a') == False
        self.backend.set('a', 1, None)
        assert self.backend.has_key('a') == False

    def test_get_many(self):
        assert self.backend.get_many('a', 'b', 'c') == [MISSING_KEY] * 3

    def test_set_many(self):
        assert self.backend.set_many({'a': 1, 'b': 2, 'c': 3}.items(), None) is None
        assert self.backend.get_many('a', 'b', 'c') == [MISSING_KEY] * 3

    def test_delete_many(self):
        assert self.backend.delete_many('a', 'b', 'c') == [False, False, False]

    def test_get_ttl(self):
        assert self.backend.get_ttl('a') == MISSING_KEY
        self.backend.set('a', 1)
        assert self.backend.get_ttl('a') == MISSING_KEY
        self.backend.set_ttl('a', 300)
        assert self.backend.get_ttl('a') == MISSING_KEY


class AbstractBackendTest:

    def test_get_set(self):
        assert self.backend.get('a') is MISSING_KEY

        self.backend.set('a', 1)
        assert self.backend.get('a') == 1
        assert self.backend.get_ttl('a') == None

        self.backend.set('a', 1, 20)
        assert self.backend.get_ttl('a') == 20
        assert self.backend.get('a') == 1

    def test_add(self):
        assert self.backend.add('a', 1) == True
        assert self.backend.add('a', 1) == False

        assert self.backend.add('b', 2, 300) == True
        assert self.backend.add('b', 2, 300) == False

    def test_delete(self):
        assert self.backend.delete('a') == False

        self.backend.set('a', 1)
        assert self.backend.delete('a') == True
        assert self.backend.get('a') is MISSING_KEY
        
    def test_has_key(self):
        assert self.backend.has_key('a') == False
        self.backend.set('a', 1)
        assert self.backend.has_key('a') == True
        self.backend.set('a', 1, 1)
        time.sleep(1)
        assert self.backend.has_key('a') == False

    def test_get_set_ttl(self):
        assert self.backend.get_ttl('a') is MISSING_KEY

        self.backend.set('a', 1)
        assert self.backend.get_ttl('a') is None

        self.backend.set_ttl('a', 300)
        time.sleep(1)
        assert self.backend.get_ttl('a') == 299

    def test_get_set_many(self):
        assert self.backend.get_many('a', 'b', 'c') == [MISSING_KEY] * 3

        self.backend.set_many([('a', 1), ('b', 2), ('c', 3)])
        assert self.backend.get_many('a', 'b', 'c') == [1, 2, 3]
        for k in ['a', 'b', 'c']:
            assert self.backend.get_ttl(k) is None

        self.backend.set_many({'a': 1, 'b': 2, 'c': 3}.items(), 300)
        assert self.backend.get_many('a', 'b', 'c') == [1, 2, 3]
        for k in ['a', 'b', 'c']:
            assert self.backend.get_ttl(k) == 300

    def test_delete_many(self):
        self.backend.set_many({'a': 1, 'b': 2, 'c': 3}.items())
        assert self.backend.delete_many('a', 'b', 'c') == [True] * 3
        assert self.backend.get_many('a', 'b', 'c') == [MISSING_KEY] * 3

    def test_incr_decr(self):
        assert self.backend.incr('a') == 1
        assert self.backend.incr('b', 20) == 20

        assert self.backend.decr('a') == 0
        assert self.backend.decr('b', 5) == 15


class TestLocalBackend(unittest.TestCase, AbstractBackendTest):
    def setUp(self):
        self.backend = LocalBackend()


class TestFileBackend(unittest.TestCase, AbstractBackendTest):
    def setUp(self):
        home_dir = os.environ['HOME']
        dir = os.path.join(home_dir, 'cachecore-tests')
        self.backend = FileBackend(dir=dir)

        for fname in os.listdir(dir):
            if fname.endswith('.cachecore'):
                fpath = os.path.join(dir, fname)
                os.remove(fpath)


class TestRedisBackend(unittest.TestCase, AbstractBackendTest):
    def setUp(self):
        client = redis.Redis()
        client.flushdb()
        self.backend = RedisBackend(client=client)


if __name__ == '__main__':
    unittest.main()