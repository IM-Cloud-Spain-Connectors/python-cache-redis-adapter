# Python Cache Redis Adapter

[![Test and Analysis](https://github.com/othercodes/python-cache-redis-adapter/actions/workflows/test.yml/badge.svg)](https://github.com/othercodes/python-cache-redis-adapter/actions/workflows/test.yml)

Provides a Redis implementation of the Cache Interface for Python.

## Installation

The easiest way to install the Cache Redis Adapter is to get the latest version from PyPI:

```bash
# using poetry
poetry add rndi-cache-redis-adapter
# using pip
pip install rndi-cache-redis-adapter
```

## The Contract

The used interface is `rndi.cache.contracts.Cache`.

## The Adapter

Just initialize the class you want and use the public methods:

```python
from rndi.cache.contracts import Cache
from rndi.cache.adapters.redis.adapter import RedisCacheAdapter


def some_process_that_requires_cache(cache: Cache):
    # retrieve the data from cache, ir the key is not cached yet and the default 
    # value is a callable the cache will use it to compute and cache the value
    user = cache.get('user-id', lambda: db_get_user('user-id'))

    print(user)


# inject the desired cache adapter.
cache = RedisCacheAdapter(
    'localhost',
    'username', 
    'password',
    database=0, # optional, 
    ttl=900, # optional
    port=5432 # optional
)
some_process_that_requires_cache(cache)
```

