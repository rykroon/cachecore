import shelve
from .local import LocalCache

"""
NOTE
- possibly choose between storing as json or msgpack?
- although the client should be naive to the serialization
- make sure I understand how it is currently implemented
"""


class FileCache(LocalCache):

    def __init__(self, filename: str):
        self._data = shelve.open(filename)

