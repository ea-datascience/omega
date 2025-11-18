"""Serialization utilities for cache data."""
import json
import pickle
import zlib
import logging
from typing import Any, Optional, Union, Type
from datetime import datetime, date, timedelta
from decimal import Decimal
from enum import Enum
import msgpack


logger = logging.getLogger(__name__)


class SerializationError(Exception):
    """Serialization error exception."""
    pass


class CacheSerializer:
    """Base serializer for cache data."""
    
    def serialize(self, data: Any) -> bytes:
        """Serialize data to bytes."""
        raise NotImplementedError
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to data."""
        raise NotImplementedError


class JSONSerializer(CacheSerializer):
    """JSON serializer with custom encoder for complex types."""
    
    class CustomJSONEncoder(json.JSONEncoder):
        """Custom JSON encoder for complex types."""
        
        def default(self, obj):
            if isinstance(obj, datetime):
                return {"__datetime__": obj.isoformat()}
            elif isinstance(obj, date):
                return {"__date__": obj.isoformat()}
            elif isinstance(obj, timedelta):
                return {"__timedelta__": obj.total_seconds()}
            elif isinstance(obj, Decimal):
                return {"__decimal__": str(obj)}
            elif isinstance(obj, Enum):
                return {"__enum__": {"class": f"{obj.__class__.__module__}.{obj.__class__.__name__}", "value": obj.value}}
            elif isinstance(obj, set):
                return {"__set__": list(obj)}
            elif isinstance(obj, bytes):
                return {"__bytes__": obj.hex()}
            return super().default(obj)
    
    def _decode_object(self, obj):
        """Custom JSON decoder for complex types."""
        if isinstance(obj, dict):
            if "__datetime__" in obj:
                return datetime.fromisoformat(obj["__datetime__"])
            elif "__date__" in obj:
                return date.fromisoformat(obj["__date__"])
            elif "__timedelta__" in obj:
                return timedelta(seconds=obj["__timedelta__"])
            elif "__decimal__" in obj:
                return Decimal(obj["__decimal__"])
            elif "__set__" in obj:
                return set(obj["__set__"])
            elif "__bytes__" in obj:
                return bytes.fromhex(obj["__bytes__"])
            elif "__enum__" in obj:
                # Note: This requires the enum class to be importable
                enum_info = obj["__enum__"]
                module_name, class_name = enum_info["class"].rsplit(".", 1)
                try:
                    module = __import__(module_name, fromlist=[class_name])
                    enum_class = getattr(module, class_name)
                    return enum_class(enum_info["value"])
                except (ImportError, AttributeError):
                    logger.warning(f"Could not deserialize enum {enum_info['class']}")
                    return enum_info["value"]
        return obj
    
    def serialize(self, data: Any) -> bytes:
        """Serialize data to JSON bytes."""
        try:
            json_str = json.dumps(data, cls=self.CustomJSONEncoder, ensure_ascii=False, separators=(',', ':'))
            return json_str.encode('utf-8')
        except (TypeError, ValueError) as e:
            raise SerializationError(f"JSON serialization failed: {e}")
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize JSON bytes to data."""
        try:
            json_str = data.decode('utf-8')
            return json.loads(json_str, object_hook=self._decode_object)
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise SerializationError(f"JSON deserialization failed: {e}")


class PickleSerializer(CacheSerializer):
    """Pickle serializer for Python objects."""
    
    def __init__(self, protocol: int = pickle.HIGHEST_PROTOCOL):
        self.protocol = protocol
    
    def serialize(self, data: Any) -> bytes:
        """Serialize data using pickle."""
        try:
            return pickle.dumps(data, protocol=self.protocol)
        except (pickle.PickleError, TypeError) as e:
            raise SerializationError(f"Pickle serialization failed: {e}")
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize pickle data."""
        try:
            return pickle.loads(data)
        except (pickle.PickleError, TypeError) as e:
            raise SerializationError(f"Pickle deserialization failed: {e}")


class MsgPackSerializer(CacheSerializer):
    """MessagePack serializer for efficient binary serialization."""
    
    def serialize(self, data: Any) -> bytes:
        """Serialize data using MessagePack."""
        try:
            return msgpack.packb(data, use_bin_type=True, datetime=True)
        except (msgpack.PackException, TypeError) as e:
            raise SerializationError(f"MessagePack serialization failed: {e}")
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize MessagePack data."""
        try:
            return msgpack.unpackb(data, raw=False, timestamp=3)
        except (msgpack.UnpackException, TypeError) as e:
            raise SerializationError(f"MessagePack deserialization failed: {e}")


class CompressedSerializer(CacheSerializer):
    """Wrapper serializer that adds compression."""
    
    def __init__(self, base_serializer: CacheSerializer, compression_level: int = 6):
        self.base_serializer = base_serializer
        self.compression_level = compression_level
    
    def serialize(self, data: Any) -> bytes:
        """Serialize and compress data."""
        try:
            serialized = self.base_serializer.serialize(data)
            return zlib.compress(serialized, self.compression_level)
        except Exception as e:
            raise SerializationError(f"Compressed serialization failed: {e}")
    
    def deserialize(self, data: bytes) -> Any:
        """Decompress and deserialize data."""
        try:
            decompressed = zlib.decompress(data)
            return self.base_serializer.deserialize(decompressed)
        except Exception as e:
            raise SerializationError(f"Compressed deserialization failed: {e}")


class SerializerRegistry:
    """Registry for different serializers."""
    
    _serializers = {
        'json': JSONSerializer(),
        'pickle': PickleSerializer(),
        'msgpack': MsgPackSerializer(),
        'compressed_json': CompressedSerializer(JSONSerializer()),
        'compressed_pickle': CompressedSerializer(PickleSerializer()),
        'compressed_msgpack': CompressedSerializer(MsgPackSerializer())
    }
    
    @classmethod
    def register(cls, name: str, serializer: CacheSerializer) -> None:
        """Register a new serializer."""
        cls._serializers[name] = serializer
    
    @classmethod
    def get(cls, name: str) -> CacheSerializer:
        """Get a serializer by name."""
        if name not in cls._serializers:
            raise ValueError(f"Unknown serializer: {name}")
        return cls._serializers[name]
    
    @classmethod
    def list_serializers(cls) -> list[str]:
        """List available serializers."""
        return list(cls._serializers.keys())


def get_serializer(name: str = 'json') -> CacheSerializer:
    """Get a serializer instance."""
    return SerializerRegistry.get(name)


def auto_serialize(data: Any) -> Tuple[bytes, str]:
    """Automatically choose the best serializer for data."""
    # Simple heuristic: try JSON first, fall back to pickle
    try:
        serializer = get_serializer('json')
        serialized = serializer.serialize(data)
        return serialized, 'json'
    except SerializationError:
        try:
            serializer = get_serializer('pickle')
            serialized = serializer.serialize(data)
            return serialized, 'pickle'
        except SerializationError:
            raise SerializationError("Could not serialize data with any available serializer")