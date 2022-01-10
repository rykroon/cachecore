import json
import pickle


class BaseSerializer:

    def dump(self, value, file):
        raise NotImplementedError

    def load(self, file):
        raise NotImplementedError

    def dumps(self, value):
        raise NotImplementedError

    def loads(self, value):
        raise NotImplementedError


class PassthroughSerializer(BaseSerializer):

    def dumps(self, value):
        return value

    def loads(self, value):
        return value


class JsonSerializer(BaseSerializer):

    def __init__(self, encoder=None, decoder=None):
        self.encoder = encoder
        self.decoder = decoder

    def dump(self, value, file):
        return json.dump(value, file, cls=self.encoder)

    def load(self, file):
        return json.load(file, cls=self.decoder)

    def dumps(self, value):
        return json.dumps(value, cls=self.encoder)

    def loads(self, value):
        return json.loads(value, cls=self.decoder)


class PickleSerializer(BaseSerializer):

    def __init__(self, protocol=pickle.DEFAULT_PROTOCOL):
        self.protocol = protocol

    def dump(self, value, file):
        return pickle.dump(value, file, protocol=self.protocol)

    def load(self, file):
        return pickle.load(file)

    def dumps(self, value):
        return pickle.dumps(value, protocol=self.protocol)

    def loads(self, value):
        return pickle.loads(value)


class RedisSerializer(PickleSerializer):

    def dumps(self, value):
        if type(value) == int:
            return value
        return super().dumps(value)

    def loads(self, value):
        try:
            return int(value)
        except ValueError:
            return super().loads(value)
