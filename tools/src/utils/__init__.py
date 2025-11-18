"""
Omega Utilities Module

Common utilities for Omega project development and analysis.

Available modules:
- java_utils: Java environment detection, validation, and management
- service_utils: Infrastructure service connection management
- parser_manager: Java parser installation and evaluation (reproducible)

All utilities follow reproducibility principles:
- Scripted installations with version pinning
- Comprehensive documentation
- Automated testing
- No ad-hoc configurations
"""

from .java_utils import (
    JavaEnvironment,
    JavaEnvironmentManager,
    JavaSetupError,
    get_java_environment,
    validate_java_setup,
    require_java
)

from .service_utils import (
    ServiceConfig,
    ServiceConnectionError,
    get_service_config,
    get_postgres_connection_string,
    get_postgres_async_connection_string,
    check_all_services
)

from .parser_manager import (
    ParserType,
    ParserInfo,
    JavaParserManager,
    install_recommended_parser
)

__all__ = [
    # Java utilities
    'JavaEnvironment',
    'JavaEnvironmentManager',
    'JavaSetupError',
    'get_java_environment',
    'validate_java_setup',
    'require_java',
    # Service utilities
    'ServiceConfig',
    'ServiceConnectionError',
    'get_service_config',
    'get_postgres_connection_string',
    'get_postgres_async_connection_string',
    'check_all_services',
    # Parser management utilities
    'ParserType',
    'ParserInfo',
    'JavaParserManager',
    'install_recommended_parser',
]
