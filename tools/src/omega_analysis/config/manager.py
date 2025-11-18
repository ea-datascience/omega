"""Configuration management with hot-reload capabilities."""
import os
import json
import yaml
from typing import Dict, Any, Optional, Callable, Set
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import logging
from functools import lru_cache

from .settings import Settings


logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Configuration error exception."""
    pass


class ConfigFileHandler(FileSystemEventHandler):
    """File system event handler for configuration changes."""
    
    def __init__(self, config_manager: 'ConfigurationManager'):
        self.config_manager = config_manager
        self.last_modified = {}
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Check if this is a config file we're watching
        if file_path not in self.config_manager.watched_files:
            return
        
        # Debounce rapid file changes
        import time
        current_time = time.time()
        last_time = self.last_modified.get(file_path, 0)
        
        if current_time - last_time < 1.0:  # 1 second debounce
            return
        
        self.last_modified[file_path] = current_time
        
        logger.info(f"Configuration file changed: {file_path}")
        
        try:
            self.config_manager.reload_configuration()
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")


class ConfigurationManager:
    """Configuration manager with hot-reload support."""
    
    def __init__(self, config_files: Optional[list] = None, watch_files: bool = True):
        self.config_files = config_files or []
        self.watch_files = watch_files
        self.watched_files: Set[Path] = set()
        self.observers: list = []
        self.reload_callbacks: list[Callable] = []
        self.lock = threading.RLock()
        self._settings: Optional[Settings] = None
        
        # Load initial configuration
        self.reload_configuration()
        
        # Start file watching if enabled
        if self.watch_files:
            self.start_watching()
    
    def add_config_file(self, file_path: str) -> None:
        """Add a configuration file to watch."""
        path = Path(file_path)
        if path.exists():
            self.config_files.append(str(path))
            self.watched_files.add(path)
            
            if self.watch_files:
                self._watch_file(path)
    
    def add_reload_callback(self, callback: Callable) -> None:
        """Add a callback to be called when configuration is reloaded."""
        self.reload_callbacks.append(callback)
    
    def _watch_file(self, file_path: Path) -> None:
        """Start watching a specific file."""
        observer = Observer()
        handler = ConfigFileHandler(self)
        observer.schedule(handler, str(file_path.parent), recursive=False)
        observer.start()
        self.observers.append(observer)
    
    def start_watching(self) -> None:
        """Start watching configuration files for changes."""
        if not self.watch_files:
            return
        
        for config_file in self.config_files:
            path = Path(config_file)
            if path.exists():
                self.watched_files.add(path)
                self._watch_file(path)
    
    def stop_watching(self) -> None:
        """Stop watching configuration files."""
        for observer in self.observers:
            observer.stop()
            observer.join()
        self.observers.clear()
    
    def _load_file_config(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from a file."""
        path = Path(file_path)
        
        if not path.exists():
            logger.warning(f"Configuration file not found: {file_path}")
            return {}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() in ['.yml', '.yaml']:
                    return yaml.safe_load(f) or {}
                elif path.suffix.lower() == '.json':
                    return json.load(f) or {}
                else:
                    logger.warning(f"Unsupported configuration file format: {file_path}")
                    return {}
        except Exception as e:
            logger.error(f"Failed to load configuration file {file_path}: {e}")
            raise ConfigurationError(f"Failed to load {file_path}: {e}")
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def reload_configuration(self) -> None:
        """Reload configuration from all sources."""
        with self.lock:
            try:
                # Start with empty configuration
                merged_config = {}
                
                # Load and merge file configurations
                for config_file in self.config_files:
                    file_config = self._load_file_config(config_file)
                    merged_config = self._merge_configs(merged_config, file_config)
                
                # Set environment variables from merged config
                self._set_environment_variables(merged_config)
                
                # Create new settings instance
                old_settings = self._settings
                self._settings = Settings()
                
                logger.info("Configuration reloaded successfully")
                
                # Call reload callbacks
                for callback in self.reload_callbacks:
                    try:
                        callback(old_settings, self._settings)
                    except Exception as e:
                        logger.error(f"Reload callback failed: {e}")
                
            except Exception as e:
                logger.error(f"Failed to reload configuration: {e}")
                raise
    
    def _set_environment_variables(self, config: Dict[str, Any], prefix: str = "") -> None:
        """Set environment variables from configuration dictionary."""
        for key, value in config.items():
            env_key = f"{prefix}{key.upper()}" if prefix else key.upper()
            
            if isinstance(value, dict):
                self._set_environment_variables(value, f"{env_key}_")
            elif isinstance(value, (list, tuple)):
                os.environ[env_key] = ",".join(str(v) for v in value)
            elif value is not None:
                os.environ[env_key] = str(value)
    
    @property
    def settings(self) -> Settings:
        """Get current settings."""
        if self._settings is None:
            raise ConfigurationError("Configuration not loaded")
        return self._settings
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value."""
        try:
            keys = key.split('.')
            value = self.settings
            
            for k in keys:
                value = getattr(value, k)
            
            return value
        except (AttributeError, KeyError):
            return default
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration and return validation results."""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Validate database connection
            if not self.settings.database.password:
                validation_results["errors"].append("Database password is required")
            
            # Validate Redis connection
            if self.settings.redis.cluster_mode and not self.settings.redis.cluster_nodes:
                validation_results["errors"].append("Redis cluster nodes required when cluster mode is enabled")
            
            # Validate MinIO settings
            if not self.settings.minio.access_key or not self.settings.minio.secret_key:
                validation_results["errors"].append("MinIO access key and secret key are required")
            
            # Validate security settings
            if len(self.settings.security.secret_key) < 32:
                validation_results["warnings"].append("Secret key should be at least 32 characters long")
            
            # Validate analysis settings
            if self.settings.analysis.java_home and not Path(self.settings.analysis.java_home).exists():
                validation_results["warnings"].append("JAVA_HOME path does not exist")
            
            validation_results["valid"] = len(validation_results["errors"]) == 0
            
        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Configuration validation failed: {e}")
        
        return validation_results
    
    def export_configuration(self, format: str = "yaml") -> str:
        """Export current configuration in specified format."""
        config_dict = self.settings.dict()
        
        if format.lower() == "json":
            return json.dumps(config_dict, indent=2, default=str)
        elif format.lower() in ["yml", "yaml"]:
            return yaml.dump(config_dict, default_flow_style=False, default_style=None)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def __del__(self):
        """Cleanup when manager is destroyed."""
        self.stop_watching()


# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None


@lru_cache(maxsize=1)
def get_config_manager(
    config_files: Optional[list] = None,
    watch_files: bool = True
) -> ConfigurationManager:
    """Get or create the global configuration manager."""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigurationManager(config_files, watch_files)
    
    return _config_manager


def get_settings() -> Settings:
    """Get current application settings."""
    return get_config_manager().settings


def reload_configuration() -> None:
    """Reload configuration from all sources."""
    get_config_manager().reload_configuration()