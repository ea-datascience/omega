"""Redis client and connection management."""
import json
import pickle
import asyncio
import logging
from typing import Any, Optional, Union, Dict, List, Tuple
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import redis.asyncio as redis
from redis.asyncio import ConnectionPool, Redis
from redis.asyncio.cluster import RedisCluster

from ..config.settings import RedisSettings


logger = logging.getLogger(__name__)


class RedisConnectionManager:
    """Manages Redis connections and connection pools."""
    
    def __init__(self, settings: RedisSettings):
        self.settings = settings
        self._pool: Optional[ConnectionPool] = None
        self._cluster_pool: Optional[RedisCluster] = None
        self._client: Optional[Union[Redis, RedisCluster]] = None
    
    async def initialize(self) -> None:
        """Initialize Redis connection."""
        try:
            if self.settings.cluster_mode:
                await self._initialize_cluster()
            else:
                await self._initialize_single()
            
            # Test connection
            await self.ping()
            logger.info("Redis connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis connection: {e}")
            raise
    
    async def _initialize_single(self) -> None:
        """Initialize single Redis instance connection."""
        self._pool = ConnectionPool(
            host=self.settings.host,
            port=self.settings.port,
            password=self.settings.password,
            db=self.settings.db,
            max_connections=self.settings.max_connections,
            retry_on_timeout=self.settings.retry_on_timeout,
            socket_timeout=self.settings.socket_timeout,
            socket_connect_timeout=self.settings.socket_connect_timeout,
            decode_responses=False  # We handle encoding/decoding ourselves
        )
        
        self._client = Redis(connection_pool=self._pool)
    
    async def _initialize_cluster(self) -> None:
        """Initialize Redis cluster connection."""
        if not self.settings.cluster_nodes:
            raise ValueError("Cluster nodes must be specified for cluster mode")
        
        # Parse cluster nodes
        startup_nodes = []
        for node in self.settings.cluster_nodes:
            if ':' in node:
                host, port = node.split(':', 1)
                startup_nodes.append({"host": host, "port": int(port)})
            else:
                startup_nodes.append({"host": node, "port": 6379})
        
        self._cluster_pool = RedisCluster(
            startup_nodes=startup_nodes,
            password=self.settings.password,
            max_connections=self.settings.max_connections,
            retry_on_timeout=self.settings.retry_on_timeout,
            socket_timeout=self.settings.socket_timeout,
            socket_connect_timeout=self.settings.socket_connect_timeout,
            decode_responses=False
        )
        
        self._client = self._cluster_pool
    
    async def close(self) -> None:
        """Close Redis connections."""
        if self._client:
            await self._client.close()
        
        if self._pool:
            await self._pool.disconnect()
        
        logger.info("Redis connections closed")
    
    async def ping(self) -> bool:
        """Test Redis connection."""
        if not self._client:
            return False
        
        try:
            result = await self._client.ping()
            return result is True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    @property
    def client(self) -> Union[Redis, RedisCluster]:
        """Get Redis client."""
        if not self._client:
            raise RuntimeError("Redis client not initialized")
        return self._client
    
    async def get_info(self) -> Dict[str, Any]:
        """Get Redis server information."""
        if not self._client:
            return {}
        
        try:
            info = await self._client.info()
            return info
        except Exception as e:
            logger.error(f"Failed to get Redis info: {e}")
            return {}
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        stats = {
            "cluster_mode": self.settings.cluster_mode,
            "connected": await self.ping(),
            "pool_stats": {}
        }
        
        if self._pool:
            stats["pool_stats"] = {
                "created_connections": self._pool.created_connections,
                "available_connections": len(self._pool._available_connections),
                "in_use_connections": len(self._pool._in_use_connections)
            }
        
        return stats