import json
import pickle
import unittest

from cachecore.serializers import PassthroughSerializer, StringSerializer, JsonSerializer, PickleSerializer


class TestPassthroughSerializer(unittest.TestCase):

    def test_dumps(self):
        serializer = PassthroughSerializer()
        values = [None, 'foo', 1, 1.23, True, [], {}, object()]
        for value in values:
            assert serializer.dumps(value) == value

    def test_loads(self):
        serializer = PassthroughSerializer()
        values = [None, 'foo', 1, 1.23, True, [], {}, object()]
        for value in values:
            assert serializer.loads(value) == value


class TestStringSerializer(unittest.TestCase):

    def test_dumps(self):
        serializer = StringSerializer()
        values = [None, 'foo', 1, 1.23, True, [], {}, object()]
        for value in values:
            assert serializer.dumps(value) == str(value)

    def test_loads(self):
        serializer = StringSerializer()
        values = ['None', 'foo', '1', '1.23', 'True', '[]', '{}']
        for value in values:
            assert serializer.loads(value) == value


class TestJsonSerializer(unittest.TestCase):
    def test_dumps(self):
        serializer = JsonSerializer()
        values = [None, 'foo', 1, 1.23, True, [], {}]
        for value in values:
            assert serializer.dumps(value) == json.dumps(value)

    def test_loads(self):
        serializer = JsonSerializer()
        values = [None, 'foo', 1, 1.23, True, [], {}]
        values = [json.dumps(v) for v in values]

        for value in values:
            assert serializer.loads(value) == json.loads(value)


class TestPickleSerializer(unittest.TestCase):
    def test_dumps(self):
        serializer = PickleSerializer()
        values = [None, 'foo', 1, 1.23, True, [], {}, object()]
        for value in values:
            assert serializer.dumps(value) == pickle.dumps(value)

    def test_loads(self):
        serializer = PickleSerializer()
        values = [None, 'foo', 1, 1.23, True, [], {}]
        values = [pickle.dumps(v) for v in values]

        for value in values:
            assert serializer.loads(value) == pickle.loads(value)


if __name__ == '__main__':
    unittest.run()
