"""Object storage service with advanced file management features."""
import asyncio
import hashlib
import logging
import mimetypes
from typing import Optional, Dict, Any, List, Union, BinaryIO, AsyncGenerator, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from io import BytesIO
import tempfile
import shutil

from minio.error import S3Error
from minio.commonconfig import Tags
from minio.datatypes import Object as MinIOObject

from .minio_client import MinIOConnectionManager
from ..config.settings import MinIOSettings


logger = logging.getLogger(__name__)


class StorageObject:
    """Represents a stored object with metadata."""
    
    def __init__(
        self,
        bucket_name: str,
        object_name: str,
        size: int,
        etag: str,
        last_modified: datetime,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        self.bucket_name = bucket_name
        self.object_name = object_name
        self.size = size
        self.etag = etag
        self.last_modified = last_modified
        self.content_type = content_type
        self.metadata = metadata or {}
        self.tags = tags or {}
    
    @property
    def key(self) -> str:
        """Get full object key."""
        return f"{self.bucket_name}/{self.object_name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "bucket_name": self.bucket_name,
            "object_name": self.object_name,
            "size": self.size,
            "etag": self.etag,
            "last_modified": self.last_modified.isoformat(),
            "content_type": self.content_type,
            "metadata": self.metadata,
            "tags": self.tags
        }


class ObjectStorageService:
    """Advanced object storage service with MinIO backend."""
    
    def __init__(
        self,
        connection_manager: MinIOConnectionManager,
        default_bucket: Optional[str] = None,
        enable_versioning: bool = True,
        enable_encryption: bool = False
    ):
        self.connection_manager = connection_manager
        self.default_bucket = default_bucket or connection_manager.settings.default_bucket
        self.enable_versioning = enable_versioning
        self.enable_encryption = enable_encryption
        self._stats = {
            'uploads': 0,
            'downloads': 0,
            'deletes': 0,
            'errors': 0,
            'bytes_uploaded': 0,
            'bytes_downloaded': 0
        }
    
    def _get_content_type(self, file_path: str) -> str:
        """Get content type from file path."""
        content_type, _ = mimetypes.guess_type(file_path)
        return content_type or 'application/octet-stream'
    
    def _generate_object_name(
        self,
        original_name: str,
        prefix: Optional[str] = None,
        use_timestamp: bool = True
    ) -> str:
        """Generate object name with optional prefix and timestamp."""
        parts = []
        
        if prefix:
            parts.append(prefix.strip('/'))
        
        if use_timestamp:
            timestamp = datetime.utcnow().strftime('%Y/%m/%d')
            parts.append(timestamp)
        
        # Clean original name
        clean_name = Path(original_name).name
        parts.append(clean_name)
        
        return '/'.join(parts)
    
    async def upload_file(
        self,
        file_path: Union[str, Path],
        object_name: Optional[str] = None,
        bucket_name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
        prefix: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> StorageObject:
        """Upload a file to object storage."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            bucket = bucket_name or self.default_bucket
            
            # Generate object name if not provided
            if not object_name:
                object_name = self._generate_object_name(
                    file_path.name, prefix=prefix
                )
            
            # Determine content type
            if not content_type:
                content_type = self._get_content_type(str(file_path))
            
            # Prepare metadata
            file_metadata = metadata or {}
            file_metadata.update({
                'original_name': file_path.name,
                'uploaded_at': datetime.utcnow().isoformat(),
                'file_size': str(file_path.stat().st_size)
            })
            
            # Upload file
            loop = asyncio.get_event_loop()
            client = self.connection_manager.client
            
            result = await loop.run_in_executor(
                None,
                lambda: client.fput_object(
                    bucket,
                    object_name,
                    str(file_path),
                    content_type=content_type,
                    metadata=file_metadata,
                    tags=Tags.new_object_tags() if not tags else Tags(tags)
                )
            )
            
            # Update stats
            file_size = file_path.stat().st_size
            self._stats['uploads'] += 1
            self._stats['bytes_uploaded'] += file_size
            
            logger.info(f"Uploaded file {file_path} to {bucket}/{object_name}")
            
            # Return storage object
            return StorageObject(
                bucket_name=bucket,
                object_name=object_name,
                size=file_size,
                etag=result.etag,
                last_modified=datetime.utcnow(),
                content_type=content_type,
                metadata=file_metadata,
                tags=tags
            )
            
        except Exception as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            self._stats['errors'] += 1
            raise
    
    async def upload_data(
        self,
        data: Union[bytes, str, BinaryIO],
        object_name: str,
        bucket_name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None
    ) -> StorageObject:
        """Upload data to object storage."""
        try:
            bucket = bucket_name or self.default_bucket
            
            # Convert data to BytesIO if necessary
            if isinstance(data, str):
                data_io = BytesIO(data.encode('utf-8'))
                data_size = len(data.encode('utf-8'))
                content_type = content_type or 'text/plain'
            elif isinstance(data, bytes):
                data_io = BytesIO(data)
                data_size = len(data)
                content_type = content_type or 'application/octet-stream'
            else:
                data_io = data
                # Try to get size
                try:
                    current_pos = data_io.tell()
                    data_io.seek(0, 2)  # Seek to end
                    data_size = data_io.tell()
                    data_io.seek(current_pos)  # Restore position
                except:
                    data_size = -1
                content_type = content_type or 'application/octet-stream'
            
            # Prepare metadata
            file_metadata = metadata or {}
            file_metadata.update({
                'uploaded_at': datetime.utcnow().isoformat(),
                'data_size': str(data_size) if data_size >= 0 else 'unknown'
            })
            
            # Upload data
            loop = asyncio.get_event_loop()
            client = self.connection_manager.client
            
            result = await loop.run_in_executor(
                None,
                lambda: client.put_object(
                    bucket,
                    object_name,
                    data_io,
                    length=data_size if data_size >= 0 else -1,
                    content_type=content_type,
                    metadata=file_metadata,
                    tags=Tags.new_object_tags() if not tags else Tags(tags)
                )
            )
            
            # Update stats
            if data_size >= 0:
                self._stats['bytes_uploaded'] += data_size
            self._stats['uploads'] += 1
            
            logger.info(f"Uploaded data to {bucket}/{object_name}")
            
            return StorageObject(
                bucket_name=bucket,
                object_name=object_name,
                size=data_size if data_size >= 0 else 0,
                etag=result.etag,
                last_modified=datetime.utcnow(),
                content_type=content_type,
                metadata=file_metadata,
                tags=tags
            )
            
        except Exception as e:
            logger.error(f"Failed to upload data to {object_name}: {e}")
            self._stats['errors'] += 1
            raise
    
    async def download_file(
        self,
        object_name: str,
        local_path: Union[str, Path],
        bucket_name: Optional[str] = None
    ) -> Path:
        """Download a file from object storage."""
        try:
            bucket = bucket_name or self.default_bucket
            local_path = Path(local_path)
            
            # Ensure parent directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download file
            loop = asyncio.get_event_loop()
            client = self.connection_manager.client
            
            await loop.run_in_executor(
                None,
                lambda: client.fget_object(bucket, object_name, str(local_path))
            )
            
            # Update stats
            file_size = local_path.stat().st_size
            self._stats['downloads'] += 1
            self._stats['bytes_downloaded'] += file_size
            
            logger.info(f"Downloaded {bucket}/{object_name} to {local_path}")
            
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to download {object_name}: {e}")
            self._stats['errors'] += 1
            raise
    
    async def download_data(
        self,
        object_name: str,
        bucket_name: Optional[str] = None
    ) -> bytes:
        """Download object data as bytes."""
        try:
            bucket = bucket_name or self.default_bucket
            
            # Download data
            loop = asyncio.get_event_loop()
            client = self.connection_manager.client
            
            response = await loop.run_in_executor(
                None,
                lambda: client.get_object(bucket, object_name)
            )
            
            data = response.read()
            response.close()
            response.release_conn()
            
            # Update stats
            self._stats['downloads'] += 1
            self._stats['bytes_downloaded'] += len(data)
            
            logger.info(f"Downloaded data from {bucket}/{object_name}")
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to download data from {object_name}: {e}")
            self._stats['errors'] += 1
            raise
    
    async def get_object_info(
        self,
        object_name: str,
        bucket_name: Optional[str] = None
    ) -> Optional[StorageObject]:
        """Get object information."""
        try:
            bucket = bucket_name or self.default_bucket
            
            loop = asyncio.get_event_loop()
            client = self.connection_manager.client
            
            stat = await loop.run_in_executor(
                None,
                lambda: client.stat_object(bucket, object_name)
            )
            
            return StorageObject(
                bucket_name=bucket,
                object_name=object_name,
                size=stat.size,
                etag=stat.etag,
                last_modified=stat.last_modified,
                content_type=stat.content_type,
                metadata=stat.metadata,
                tags={}  # Tags would need separate call
            )
            
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return None
            logger.error(f"Failed to get object info for {object_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to get object info for {object_name}: {e}")
            raise
    
    async def delete_object(
        self,
        object_name: str,
        bucket_name: Optional[str] = None
    ) -> bool:
        """Delete an object."""
        try:
            bucket = bucket_name or self.default_bucket
            
            loop = asyncio.get_event_loop()
            client = self.connection_manager.client
            
            await loop.run_in_executor(
                None,
                lambda: client.remove_object(bucket, object_name)
            )
            
            self._stats['deletes'] += 1
            logger.info(f"Deleted object {bucket}/{object_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete object {object_name}: {e}")
            self._stats['errors'] += 1
            return False
    
    async def list_objects(
        self,
        prefix: Optional[str] = None,
        bucket_name: Optional[str] = None,
        recursive: bool = True,
        max_objects: Optional[int] = None
    ) -> List[StorageObject]:
        """List objects in bucket."""
        try:
            bucket = bucket_name or self.default_bucket
            
            loop = asyncio.get_event_loop()
            client = self.connection_manager.client
            
            objects = await loop.run_in_executor(
                None,
                lambda: list(client.list_objects(
                    bucket, prefix=prefix, recursive=recursive
                ))
            )
            
            # Convert to StorageObject instances
            result = []
            for obj in objects:
                if max_objects and len(result) >= max_objects:
                    break
                
                storage_obj = StorageObject(
                    bucket_name=bucket,
                    object_name=obj.object_name,
                    size=obj.size,
                    etag=obj.etag,
                    last_modified=obj.last_modified,
                    content_type=None,  # Not available in list operation
                    metadata={},
                    tags={}
                )
                result.append(storage_obj)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to list objects in bucket {bucket}: {e}")
            raise
    
    async def get_presigned_url(
        self,
        object_name: str,
        bucket_name: Optional[str] = None,
        expires: timedelta = None,
        method: str = "GET"
    ) -> str:
        """Get presigned URL for object access."""
        try:
            bucket = bucket_name or self.default_bucket
            expires = expires or timedelta(seconds=self.connection_manager.settings.presigned_url_expiry)
            
            loop = asyncio.get_event_loop()
            client = self.connection_manager.client
            
            if method.upper() == "GET":
                url = await loop.run_in_executor(
                    None,
                    lambda: client.presigned_get_object(bucket, object_name, expires)
                )
            elif method.upper() == "PUT":
                url = await loop.run_in_executor(
                    None,
                    lambda: client.presigned_put_object(bucket, object_name, expires)
                )
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            logger.info(f"Generated presigned URL for {bucket}/{object_name}")
            
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate presigned URL for {object_name}: {e}")
            raise
    
    async def copy_object(
        self,
        source_object: str,
        dest_object: str,
        source_bucket: Optional[str] = None,
        dest_bucket: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> StorageObject:
        """Copy an object to a new location."""
        try:
            source_bucket = source_bucket or self.default_bucket
            dest_bucket = dest_bucket or self.default_bucket
            
            loop = asyncio.get_event_loop()
            client = self.connection_manager.client
            
            # Prepare copy source
            from minio.commonconfig import CopySource
            copy_source = CopySource(source_bucket, source_object)
            
            result = await loop.run_in_executor(
                None,
                lambda: client.copy_object(
                    dest_bucket,
                    dest_object,
                    copy_source,
                    metadata=metadata
                )
            )
            
            logger.info(f"Copied {source_bucket}/{source_object} to {dest_bucket}/{dest_object}")
            
            # Get info about copied object
            return await self.get_object_info(dest_object, dest_bucket)
            
        except Exception as e:
            logger.error(f"Failed to copy object {source_object}: {e}")
            self._stats['errors'] += 1
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage service statistics."""
        stats = self._stats.copy()
        
        # Add connection stats
        try:
            connection_stats = await self.connection_manager.get_stats()
            stats['connection'] = connection_stats
        except Exception as e:
            stats['connection_error'] = str(e)
        
        return stats


# Global storage service instance
_storage_service: Optional[ObjectStorageService] = None


async def get_storage_service(settings: Optional[MinIOSettings] = None) -> ObjectStorageService:
    """Get or create global storage service."""
    global _storage_service
    
    if _storage_service is None:
        if settings is None:
            from ..config import get_settings
            settings = get_settings().minio
        
        connection_manager = MinIOConnectionManager(settings)
        await connection_manager.initialize()
        
        _storage_service = ObjectStorageService(connection_manager)
    
    return _storage_service