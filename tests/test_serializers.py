import json
import pickle
import unittest

from cachecore.serializers import PassthroughSerializer, RedisSerializer, JsonSerializer, PickleSerializer


class AbstractSerializerTest(unittest.TestCase):

    def setUp(self):
        self.values = [
            None, 
            'foo', 
            123, 
            1.23, 
            True,
            [None, 'foo', 123, 1.23, True],
            {
                'foo': 123,
                'bar': 1.23,
                'baz': False,
            }
        ]


class TestPassthroughSerializer(AbstractSerializerTest):

    def test_dumps_loads(self):
        serializer = PassthroughSerializer()

        for value in self.values:
            svalue = serializer.dumps(value)
            assert type(svalue) == type(value)
            assert serializer.loads(svalue) == value


class TestJsonSerializer(AbstractSerializerTest):
    def test_dumps_loads(self):
        serializer = JsonSerializer()

        for value in self.values:
            svalue = serializer.dumps(value)
            assert type(svalue) == str
            assert serializer.loads(svalue) == value


class TestPickleSerializer(AbstractSerializerTest):
    def test_dumps_loads(self):
        serializer = PickleSerializer()

        for value in self.values:
            svalue = serializer.dumps(value)
            assert type(svalue) == bytes
            assert serializer.loads(svalue) == value


class TestRedisSerializer(AbstractSerializerTest):
    def test_dumps_loads(self):
        serializer = RedisSerializer()

        for value in self.values:
            svalue = serializer.dumps(value)
            assert type(svalue) in [bytes, int]
            assert serializer.loads(svalue) == value

        assert serializer.dumps(20) == 20
        assert serializer.loads(20) == 20


if __name__ == '__main__':
    unittest.run()
