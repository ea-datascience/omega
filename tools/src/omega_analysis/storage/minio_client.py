"""MinIO client and connection management."""
import asyncio
import logging
from typing import Optional, Dict, Any, List, Union, BinaryIO, AsyncGenerator
from datetime import datetime, timedelta
from pathlib import Path
import mimetypes
from contextlib import asynccontextmanager

from minio import Minio
from minio.error import S3Error, BucketAlreadyOwnedByYou, BucketAlreadyExists
from minio.commonconfig import Tags
from minio.lifecycleconfig import LifecycleConfig, Rule, Expiration
from urllib3 import PoolManager

from ..config.settings import MinIOSettings


logger = logging.getLogger(__name__)


class MinIOConnectionManager:
    """Manages MinIO connections and bucket operations."""
    
    def __init__(self, settings: MinIOSettings):
        self.settings = settings
        self._client: Optional[Minio] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize MinIO client."""
        try:
            # Create MinIO client
            self._client = Minio(
                endpoint=self.settings.endpoint,
                access_key=self.settings.access_key,
                secret_key=self.settings.secret_key,
                secure=self.settings.secure,
                region=self.settings.region,
                http_client=PoolManager(
                    timeout=30,
                    retries=3
                )
            )
            
            # Test connection
            await self._test_connection()
            
            # Ensure default bucket exists
            await self._ensure_bucket_exists(self.settings.default_bucket)
            
            self._initialized = True
            logger.info("MinIO connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MinIO connection: {e}")
            raise
    
    async def _test_connection(self) -> None:
        """Test MinIO connection."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, list, self._client.list_buckets())
        except Exception as e:
            raise ConnectionError(f"MinIO connection test failed: {e}")
    
    async def _ensure_bucket_exists(self, bucket_name: str) -> None:
        """Ensure bucket exists, create if not."""
        try:
            loop = asyncio.get_event_loop()
            exists = await loop.run_in_executor(
                None, self._client.bucket_exists, bucket_name
            )
            
            if not exists:
                await loop.run_in_executor(
                    None, self._client.make_bucket, bucket_name
                )
                logger.info(f"Created MinIO bucket: {bucket_name}")
            
        except (BucketAlreadyOwnedByYou, BucketAlreadyExists):
            pass  # Bucket already exists
        except Exception as e:
            logger.error(f"Failed to ensure bucket {bucket_name} exists: {e}")
            raise
    
    @property
    def client(self) -> Minio:
        """Get MinIO client."""
        if not self._client or not self._initialized:
            raise RuntimeError("MinIO client not initialized")
        return self._client
    
    async def get_bucket_info(self, bucket_name: str) -> Dict[str, Any]:
        """Get bucket information."""
        try:
            loop = asyncio.get_event_loop()
            
            # Check if bucket exists
            exists = await loop.run_in_executor(
                None, self._client.bucket_exists, bucket_name
            )
            
            if not exists:
                return {"exists": False}
            
            # Get bucket info
            info = {
                "exists": True,
                "name": bucket_name,
                "creation_date": None,
                "location": None
            }
            
            # Get bucket location
            try:
                location = await loop.run_in_executor(
                    None, self._client.get_bucket_location, bucket_name
                )
                info["location"] = location
            except Exception:
                pass
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get bucket info for {bucket_name}: {e}")
            return {"exists": False, "error": str(e)}
    
    async def list_buckets(self) -> List[Dict[str, Any]]:
        """List all buckets."""
        try:
            loop = asyncio.get_event_loop()
            buckets = await loop.run_in_executor(None, self._client.list_buckets)
            
            return [
                {
                    "name": bucket.name,
                    "creation_date": bucket.creation_date.isoformat() if bucket.creation_date else None
                }
                for bucket in buckets
            ]
            
        except Exception as e:
            logger.error(f"Failed to list buckets: {e}")
            return []
    
    async def create_bucket(
        self,
        bucket_name: str,
        location: Optional[str] = None
    ) -> bool:
        """Create a new bucket."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._client.make_bucket, bucket_name, location or self.settings.region
            )
            logger.info(f"Created bucket: {bucket_name}")
            return True
            
        except (BucketAlreadyOwnedByYou, BucketAlreadyExists):
            logger.info(f"Bucket already exists: {bucket_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create bucket {bucket_name}: {e}")
            return False
    
    async def delete_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """Delete a bucket."""
        try:
            loop = asyncio.get_event_loop()
            
            if force:
                # Delete all objects first
                await self._delete_all_objects(bucket_name)
            
            await loop.run_in_executor(None, self._client.remove_bucket, bucket_name)
            logger.info(f"Deleted bucket: {bucket_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete bucket {bucket_name}: {e}")
            return False
    
    async def _delete_all_objects(self, bucket_name: str) -> None:
        """Delete all objects in a bucket."""
        try:
            loop = asyncio.get_event_loop()
            
            # List all objects
            objects = await loop.run_in_executor(
                None,
                lambda: list(self._client.list_objects(bucket_name, recursive=True))
            )
            
            # Delete objects in batches
            if objects:
                object_names = [obj.object_name for obj in objects]
                errors = await loop.run_in_executor(
                    None,
                    lambda: list(self._client.remove_objects(bucket_name, object_names))
                )
                
                for error in errors:
                    logger.error(f"Failed to delete object {error.object_name}: {error}")
                    
        except Exception as e:
            logger.error(f"Failed to delete all objects in bucket {bucket_name}: {e}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get MinIO connection statistics."""
        stats = {
            "initialized": self._initialized,
            "endpoint": self.settings.endpoint,
            "secure": self.settings.secure,
            "region": self.settings.region,
            "default_bucket": self.settings.default_bucket
        }
        
        if self._initialized:
            try:
                buckets = await self.list_buckets()
                stats["bucket_count"] = len(buckets)
                stats["buckets"] = buckets
            except Exception as e:
                stats["error"] = str(e)
        
        return stats