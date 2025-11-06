# SPDX-FileCopyrightText: 2025-present Ryan Kroon <rykroon.tech@gmail.com>
#
# SPDX-License-Identifier: MIT
from .interface import CacheInterface
from .base import BaseCache
from .dummy import DummyCache
from .file import FileCache
from .local import LocalCache
from .memcached import MemcachedCache
from .redis import RedisCache


"""
NOTE
- use hatch for package management
- greatly simplify
  - only define get, set, del, has (__contains__), size (__len__), clear.
  - maybe pop and popitem
  - See Mapping and Mutable Mapping (https://docs.python.org/3/library/collections.abc.html)
  - fuck memcached
  - valkey instead of redis?

"""


