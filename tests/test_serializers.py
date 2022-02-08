import pickle
import unittest

from pycachecore.serializers import RedisSerializer, Serializer



class TestSerializerInterface(unittest.TestCase):

    def test_all(self):
        assert isinstance(pickle, Serializer)
        assert issubclass(RedisSerializer, Serializer)


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
            assert type(svalue) in [bytes, int]
            assert serializer.loads(svalue) == value

        assert serializer.dumps(20) == 20
        assert serializer.loads(20) == 20


if __name__ == '__main__':
    unittest.run()
