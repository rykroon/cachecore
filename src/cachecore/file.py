import shelve
from .local import DictCache

"""
NOTE
- possibly choose between storing as json or msgpack?
- although the client should be naive to the serialization
"""


class FileCache(DictCache):

    def __init__(self, filename: str):
        self._data = shelve.open(filename)

