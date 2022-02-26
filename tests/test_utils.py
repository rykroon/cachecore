import os
import unittest

from cachecore.utils import Directory


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