#
# This file is part of the Ingram Micro CloudBlue RnD Integration Connectors SDK.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
import time
from typing import Any, Optional

import jsonpickle
import redis
from rndi.cache.contracts import Cache


def provide_redis_cache_adapter(config: dict) -> Cache:
    return RedisCacheAdapter(
        host=config.get('CACHE_REDIS_HOST', 'localhost'),
        port=config.get('CACHE_REDIS_PORT', 'cache'),
        database=config.get('CACHE_REDIS_DB', 0),
        username=config.get('CACHE_REDIS_USERNAME', None),
        password=config.get('CACHE_REDIS_PASSWORD', None),
        ttl=config.get('CACHE_TTL', 900),
        encoding=config.get('CACHE_REDIS_ENCODING', 'utf-8'),
    )


class RedisCacheAdapter(Cache):
    _connection = None

    def __init__(
            self,
            host: str,
            username: str = None,
            password: str = None,
            database: int = 0,
            ttl: int = 900,
            port: int = 6379,
            encoding: str = 'utf-8',
    ):
        self.database = database
        self.host = host
        self.ttl = ttl
        self.port = port
        self.username = username
        self.password = password
        self.encoding = encoding

    @property
    def connection(self) -> redis.Redis:
        """
        Returns the Connection object.
        :return: connection
        """
        if self._connection:
            return self._connection

        self._connection = redis.Redis(
            host=self.host,
            db=self.database,
            port=self.port,
            username=self.username,
            password=self.password,
        )

        return self._connection

    def has(self, key: str) -> bool:
        return self.connection.exists(key) > 0

    def get(self, key: str, default: Any = None, ttl: Optional[int] = None) -> Any:
        try:
            entry = self.connection.get(key)

            if entry is None:
                raise StopIteration

            if ttl is not None:
                self.connection.getex(key, exat=round(time.time()) + ttl)

            return jsonpickle.decode(entry.decode(self.encoding))
        except StopIteration:
            ttl = ttl if ttl else self.ttl
            value = default() if callable(default) else default

            if isinstance(value, tuple):
                value, ttl = value

        return value if value is None else self.put(key, value, ttl)

    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> Any:
        serialized = jsonpickle.encode(value)
        expire_at = (self.ttl if ttl is None else ttl) + round(time.time())
        self.connection.set(key, serialized, exat=expire_at)

        return value

    def delete(self, key: str) -> None:
        self.connection.delete(key)

    def flush(self, expired_only: bool = False) -> None:
        if not expired_only:
            self.connection.flushall()

    def __del__(self):
        if self.connection:
            self.connection.close()
