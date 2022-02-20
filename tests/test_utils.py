import os
import unittest
import time

from cachecore.utils import Value, MISSING_KEY, MissingKey, Directory


class TestMissingKey(unittest.TestCase):
    def test_missing_key(self):
        assert MISSING_KEY is MissingKey()


class TestValue(unittest.TestCase):
    def test_value(self):
        v = Value(10, None)
        assert v.ttl is None
        assert v.is_expired() is False

        v.ttl = 1
        assert v.ttl == 1
        time.sleep(1)
        assert v.ttl == 0
        assert v.is_expired() is True


class TestDirectory(unittest.TestCase):
    def setUp(self):
        home_dir = os.environ['HOME']
        path = os.path.join(home_dir, 'cachecore-tests')
        self.dir = Directory(path)

    def test_directory(self):
        self.dir['a.txt'] = b'hello world'
        assert self.dir['a.txt'] == b'hello world'
        assert ('a.txt' in self.dir) is True
        del self.dir['a.txt']

        with self.assertRaises(KeyError):
            self.dir['a.txt']

        with self.assertRaises(KeyError):
            del self.dir['a.txt']

        assert ('a.txt' in self.dir) is False


if __name__ == '__main__':
    unittest.main()