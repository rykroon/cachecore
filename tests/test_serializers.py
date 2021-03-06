import pickle
import unittest

from src.cachecore.serializers import JSONSerializer, RedisSerializer, SerializerInterface



class TestSerializerInterface(unittest.TestCase):

    def test_all(self):
        assert isinstance(pickle, SerializerInterface)
        assert issubclass(JSONSerializer, SerializerInterface)
        assert issubclass(RedisSerializer, SerializerInterface)


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


class TestRedisSerializer(AbstractSerializerTest):
    def test_dumps_loads(self):
        serializer = RedisSerializer()

        for value in self.values:
            svalue = serializer.dumps(value)
            assert serializer.loads(svalue) == value

        assert serializer.dumps(20) == b'20'
        assert serializer.loads(b'20') == 20


class TestJSONSerializer(AbstractSerializerTest):
    def test_dumps_loads(self):
        serializer = JSONSerializer()

        for value in self.values:
            svalue = serializer.dumps(value)
            assert serializer.loads(svalue) == value


if __name__ == '__main__':
    unittest.run()
