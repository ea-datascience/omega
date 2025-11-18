"""Object storage service with file operations and presigned URLs."""
import asyncio
import logging
from typing import Optional, Dict, Any, List, Union, BinaryIO, AsyncGenerator, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import mimetypes
from io import BytesIO, StringIO
import tempfile
import hashlib

from minio.error import S3Error
from minio.commonconfig import Tags, REPLACE
from minio.deleteobjects import DeleteObject

from .minio_client import MinIOConnectionManager
from ..config.settings import MinIOSettings


logger = logging.getLogger(__name__)


class StorageService:
    """High-level storage service for file operations."""
    
    def __init__(self, connection_manager: MinIOConnectionManager):
        self.connection_manager = connection_manager
        self.default_bucket = connection_manager.settings.default_bucket
    
    async def upload_file(
        self,
        file_path: Union[str, Path, BinaryIO],
        object_name: str,
        bucket_name: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Upload a file to object storage."""
        try:
            bucket = bucket_name or self.default_bucket
            client = self.connection_manager.client
            loop = asyncio.get_event_loop()
            
            # Determine content type
            if content_type is None:
                if isinstance(file_path, (str, Path)):
                    content_type, _ = mimetypes.guess_type(str(file_path))
                content_type = content_type or 'application/octet-stream'
            
            # Prepare metadata
            object_metadata = metadata or {}
            object_metadata.update({
                'uploaded_at': datetime.utcnow().isoformat(),
                'content_type': content_type
            })
            
            # Calculate file size and hash if it's a file path
            file_size = None
            file_hash = None
            
            if isinstance(file_path, (str, Path)):
                path_obj = Path(file_path)
                file_size = path_obj.stat().st_size
                
                # Calculate hash
                hash_md5 = hashlib.md5()
                with open(path_obj, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
                file_hash = hash_md5.hexdigest()
                object_metadata['file_hash'] = file_hash
            
            # Upload file
            result = await loop.run_in_executor(
                None,
                client.fput_object,
                bucket,
                object_name,
                str(file_path) if isinstance(file_path, (str, Path)) else file_path,
                content_type,
                object_metadata,
                None,  # server_side_encryption
                None,  # progress
                None,  # part_size
                None,  # num_parallel_uploads
                Tags(tags) if tags else None
            )
            
            logger.info(f"File uploaded successfully: {object_name} to bucket {bucket}")
            
            return {
                'success': True,
                'bucket': bucket,
                'object_name': object_name,
                'etag': result.etag,
                'version_id': result.version_id,
                'size': file_size,
                'hash': file_hash,
                'content_type': content_type,
                'metadata': object_metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to upload file {object_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'object_name': object_name,
                'bucket': bucket_name or self.default_bucket
            }
    
    async def get_presigned_url(
        self,
        object_name: str,
        bucket_name: Optional[str] = None,
        expires: timedelta = timedelta(hours=1),
        method: str = 'GET'
    ) -> Optional[str]:
        """Generate a presigned URL for object access."""
        try:
            bucket = bucket_name or self.default_bucket
            client = self.connection_manager.client
            loop = asyncio.get_event_loop()
            
            # Generate presigned URL
            if method.upper() == 'GET':
                url = await loop.run_in_executor(
                    None,
                    client.presigned_get_object,
                    bucket,
                    object_name,
                    expires
                )
            elif method.upper() == 'PUT':
                url = await loop.run_in_executor(
                    None,
                    client.presigned_put_object,
                    bucket,
                    object_name,
                    expires
                )
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            logger.info(f"Generated presigned URL for {object_name}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate presigned URL for {object_name}: {e}")
            return None


# Global storage service instance
_storage_service: Optional[StorageService] = None