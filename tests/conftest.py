from __future__ import annotations

from abc import ABCMeta, abstractmethod
from logging import LoggerAdapter
from typing import Dict, List, Optional, Union
from unittest.mock import patch

import pytest
from rndi.cache.adapters.redis.adapter import RedisCacheAdapter
from rndi.cache.contracts import Cache
from rndi.cache.provider import provide_cache


@pytest.fixture
def adapters(logger):
    def __adapters() -> List[Cache]:
        setups = [
            {
                'CACHE_DRIVER': 'redis',
                'CACHE_REDIS_HOST': 'localhost',
                'CACHE_REDIS_PORT': 6379,
            },
        ]

        extra = {
            'redis': provide_test_redis_cache_adapter,
        }

        return [provide_cache(setup, logger(), extra) for setup in setups]

    return __adapters


@pytest.fixture()
def logger():
    def __logger() -> LoggerAdapter:
        with patch('logging.LoggerAdapter') as logger:
            return logger

    return __logger


@pytest.fixture
def counter():
    class Counter:
        instance: Optional[Counter] = None

        def __init__(self):
            self.count = 0

        @classmethod
        def make(cls, reset: bool = False) -> Counter:
            if not isinstance(cls.instance, Counter) or reset:
                cls.instance = Counter()
            return cls.instance

        def increase(self, step: int = 1) -> Counter:
            self.count = self.count + step
            return self

    def __(reset: bool = False) -> Counter:
        return Counter.make(reset)

    return __


class HasEntry(metaclass=ABCMeta):  # pragma: no cover
    @abstractmethod
    def get_entry(self, key: str) -> Optional[Dict[str, Union[str, int]]]:
        """
        Get an entry from the cache, not only the value.
        This is useful for testing purposes when we want to validate the TTL.
        :param key: str The key to search for.
        :return: Optional[Dict[str, Union[str, int]]] The entry if found, None otherwise.
        """


class RedisCacheAdapterTester(RedisCacheAdapter, HasEntry):
    def get_entry(self, key: str) -> Optional[Dict[str, Union[str, int]]]:
        entry = self.connection.expiretime(key)

        if entry is None:
            return None

        return {
            'expire_at': entry,
        }


def provide_test_redis_cache_adapter(config: dict) -> Cache:
    return RedisCacheAdapterTester(
        host=config.get('CACHE_REDIS_HOST', 'localhost'),
        port=config.get('CACHE_REDIS_PORT', 'cache'),
        database=config.get('CACHE_REDIS_DB', 0),
        username=config.get('CACHE_REDIS_USERNAME', None),
        password=config.get('CACHE_REDIS_PASSWORD', None),
        ttl=config.get('CACHE_TTL', 900),
    )
