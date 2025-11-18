"""Cache manager with TTL, serialization, and advanced features."""
import asyncio
import logging
import hashlib
from typing import Any, Optional, Union, Dict, List, Callable, TypeVar, Generic
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from functools import wraps

from .redis_client import RedisConnectionManager
from .serializers import CacheSerializer, get_serializer, auto_serialize
from ..config.settings import RedisSettings


logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheEntry:
    """Represents a cached entry with metadata."""
    
    def __init__(
        self,
        key: str,
        value: Any,
        serializer: str = 'json',
        ttl: Optional[int] = None,
        created_at: Optional[datetime] = None,
        accessed_at: Optional[datetime] = None,
        hit_count: int = 0
    ):
        self.key = key
        self.value = value
        self.serializer = serializer
        self.ttl = ttl
        self.created_at = created_at or datetime.utcnow()
        self.accessed_at = accessed_at or datetime.utcnow()
        self.hit_count = hit_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'value': self.value,
            'serializer': self.serializer,
            'ttl': self.ttl,
            'created_at': self.created_at.isoformat(),
            'accessed_at': self.accessed_at.isoformat(),
            'hit_count': self.hit_count
        }
    
    @classmethod
    def from_dict(cls, key: str, data: Dict[str, Any]) -> 'CacheEntry':
        """Create from dictionary."""
        return cls(
            key=key,
            value=data['value'],
            serializer=data.get('serializer', 'json'),
            ttl=data.get('ttl'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            accessed_at=datetime.fromisoformat(data['accessed_at']) if data.get('accessed_at') else None,
            hit_count=data.get('hit_count', 0)
        )


class CacheManager:
    """Advanced cache manager with Redis backend."""
    
    def __init__(
        self,
        connection_manager: RedisConnectionManager,
        default_ttl: Optional[int] = 3600,  # 1 hour
        default_serializer: str = 'json',
        key_prefix: str = 'omega:cache:',
        enable_stats: bool = True
    ):
        self.connection_manager = connection_manager
        self.default_ttl = default_ttl
        self.default_serializer = default_serializer
        self.key_prefix = key_prefix
        self.enable_stats = enable_stats
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
    
    def _make_key(self, key: str) -> str:
        """Create full cache key with prefix."""
        return f"{self.key_prefix}{key}"
    
    def _make_meta_key(self, key: str) -> str:
        """Create metadata key."""
        return f"{self.key_prefix}meta:{key}"
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serializer: Optional[str] = None,
        if_not_exists: bool = False
    ) -> bool:
        """Set a value in cache."""
        try:
            # Determine TTL and serializer
            actual_ttl = ttl if ttl is not None else self.default_ttl
            actual_serializer = serializer or self.default_serializer
            
            # Serialize value
            if isinstance(value, bytes):
                serialized_value = value
                actual_serializer = 'bytes'
            else:
                if actual_serializer == 'auto':
                    serialized_value, actual_serializer = auto_serialize(value)
                else:
                    serializer_instance = get_serializer(actual_serializer)
                    serialized_value = serializer_instance.serialize(value)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                serializer=actual_serializer,
                ttl=actual_ttl
            )
            
            # Store in Redis
            cache_key = self._make_key(key)
            meta_key = self._make_meta_key(key)
            
            client = self.connection_manager.client
            
            # Use pipeline for atomic operations
            async with client.pipeline() as pipe:
                if if_not_exists:
                    # Set only if key doesn't exist
                    pipe.setnx(cache_key, serialized_value)
                    pipe.setnx(meta_key, get_serializer('json').serialize(entry.to_dict()))
                else:
                    pipe.set(cache_key, serialized_value)
                    pipe.set(meta_key, get_serializer('json').serialize(entry.to_dict()))
                
                if actual_ttl:
                    pipe.expire(cache_key, actual_ttl)
                    pipe.expire(meta_key, actual_ttl)
                
                results = await pipe.execute()
            
            success = results[0] if if_not_exists else True
            
            if success and self.enable_stats:
                self._stats['sets'] += 1
            
            return bool(success)
            
        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            if self.enable_stats:
                self._stats['errors'] += 1
            return False
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get a value from cache."""
        try:
            cache_key = self._make_key(key)
            meta_key = self._make_meta_key(key)
            
            client = self.connection_manager.client
            
            # Get value and metadata
            value_data, meta_data = await asyncio.gather(
                client.get(cache_key),
                client.get(meta_key),
                return_exceptions=True
            )
            
            if isinstance(value_data, Exception) or isinstance(meta_data, Exception):
                raise Exception("Failed to get cache data")
            
            if value_data is None:
                if self.enable_stats:
                    self._stats['misses'] += 1
                return default
            
            # Deserialize metadata
            if meta_data:
                try:
                    meta_dict = get_serializer('json').deserialize(meta_data)
                    entry = CacheEntry.from_dict(key, meta_dict)
                    
                    # Update access stats
                    entry.accessed_at = datetime.utcnow()
                    entry.hit_count += 1
                    
                    # Update metadata in background
                    asyncio.create_task(self._update_metadata(key, entry))
                    
                    serializer_name = entry.serializer
                except Exception as e:
                    logger.warning(f"Failed to deserialize metadata for key {key}: {e}")
                    serializer_name = self.default_serializer
            else:
                serializer_name = self.default_serializer
            
            # Deserialize value
            if serializer_name == 'bytes':
                value = value_data
            else:
                serializer_instance = get_serializer(serializer_name)
                value = serializer_instance.deserialize(value_data)
            
            if self.enable_stats:
                self._stats['hits'] += 1
            
            return value
            
        except Exception as e:
            logger.error(f"Cache get failed for key {key}: {e}")
            if self.enable_stats:
                self._stats['errors'] += 1
            return default
    
    async def _update_metadata(self, key: str, entry: CacheEntry) -> None:
        """Update metadata for cache entry."""
        try:
            meta_key = self._make_meta_key(key)
            client = self.connection_manager.client
            
            # Only update if key still exists
            ttl = await client.ttl(self._make_key(key))
            if ttl > 0:
                serialized_meta = get_serializer('json').serialize(entry.to_dict())
                await client.set(meta_key, serialized_meta, ex=ttl)
        except Exception as e:
            logger.debug(f"Failed to update metadata for key {key}: {e}")
    
    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        try:
            cache_key = self._make_key(key)
            meta_key = self._make_meta_key(key)
            
            client = self.connection_manager.client
            
            # Delete both value and metadata
            result = await client.delete(cache_key, meta_key)
            
            if self.enable_stats and result > 0:
                self._stats['deletes'] += 1
            
            return result > 0
            
        except Exception as e:
            logger.error(f"Cache delete failed for key {key}: {e}")
            if self.enable_stats:
                self._stats['errors'] += 1
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            cache_key = self._make_key(key)
            client = self.connection_manager.client
            result = await client.exists(cache_key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache exists check failed for key {key}: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for existing key."""
        try:
            cache_key = self._make_key(key)
            meta_key = self._make_meta_key(key)
            
            client = self.connection_manager.client
            
            # Set TTL for both value and metadata
            result1 = await client.expire(cache_key, ttl)
            result2 = await client.expire(meta_key, ttl)
            
            return result1 and result2
            
        except Exception as e:
            logger.error(f"Cache expire failed for key {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """Get TTL for key."""
        try:
            cache_key = self._make_key(key)
            client = self.connection_manager.client
            return await client.ttl(cache_key)
        except Exception as e:
            logger.error(f"Cache TTL check failed for key {key}: {e}")
            return -1
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries matching pattern."""
        try:
            client = self.connection_manager.client
            
            if pattern:
                search_pattern = f"{self.key_prefix}{pattern}"
            else:
                search_pattern = f"{self.key_prefix}*"
            
            # Get all matching keys
            keys = []
            async for key in client.scan_iter(match=search_pattern):
                keys.append(key)
            
            # Also get metadata keys
            meta_pattern = f"{self.key_prefix}meta:*"
            async for key in client.scan_iter(match=meta_pattern):
                keys.append(key)
            
            if keys:
                result = await client.delete(*keys)
                return result
            
            return 0
            
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = self._stats.copy()
        
        # Add hit rate
        total_requests = stats['hits'] + stats['misses']
        if total_requests > 0:
            stats['hit_rate'] = stats['hits'] / total_requests
        else:
            stats['hit_rate'] = 0.0
        
        # Add Redis connection stats
        try:
            redis_stats = await self.connection_manager.get_stats()
            stats['redis'] = redis_stats
        except Exception as e:
            logger.debug(f"Failed to get Redis stats: {e}")
        
        return stats
    
    def cache_result(
        self,
        ttl: Optional[int] = None,
        key_generator: Optional[Callable] = None,
        serializer: Optional[str] = None
    ):
        """Decorator to cache function results."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Generate cache key
                if key_generator:
                    cache_key = key_generator(*args, **kwargs)
                else:
                    # Default key generation
                    key_parts = [func.__name__]
                    key_parts.extend(str(arg) for arg in args)
                    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                    cache_key = hashlib.md5("|".join(key_parts).encode()).hexdigest()
                
                # Try to get from cache
                result = await self.get(cache_key)
                if result is not None:
                    return result
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                await self.set(cache_key, result, ttl=ttl, serializer=serializer)
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # For sync functions, we need to run in event loop
                return asyncio.create_task(async_wrapper(*args, **kwargs))
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


async def get_cache_manager(settings: Optional[RedisSettings] = None) -> CacheManager:
    """Get or create global cache manager."""
    global _cache_manager
    
    if _cache_manager is None:
        if settings is None:
            from ..config import get_settings
            settings = get_settings().redis
        
        connection_manager = RedisConnectionManager(settings)
        await connection_manager.initialize()
        
        _cache_manager = CacheManager(connection_manager)
    
    return _cache_manager