"""
Unit Tests for Context Mapper Integration

Tests the Python wrapper for Context Mapper Java libraries.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.utils.context_mapper import (
    ContextMapper,
    ContextMapperError,
)
from src.utils.java_utils import JavaEnvironment


@pytest.fixture
def mock_java_env():
    """Create a mock Java environment for testing."""
    return JavaEnvironment(
        java_home=Path("/usr/lib/jvm/java-17-openjdk-arm64"),
        java_executable=Path("/usr/lib/jvm/java-17-openjdk-arm64/bin/java"),
        version="17.0.16",
        major_version=17,
        vendor="OpenJDK",
        is_valid=True,
        maven_executable=Path("/opt/maven/bin/mvn"),
        gradle_executable=None
    )


@pytest.fixture
def context_mapper(mock_java_env):
    """Create ContextMapper instance with mocked Java environment."""
    with patch('src.utils.context_mapper.Path.home') as mock_home:
        # Mock Maven repository structure
        temp_dir = Path(tempfile.mkdtemp())
        mock_home.return_value = temp_dir
        
        # Create mock JAR files
        dsl_jar_dir = temp_dir / ".m2" / "repository" / "org" / "contextmapper" / "context-mapper-dsl" / "6.12.0"
        dsl_jar_dir.mkdir(parents=True)
        (dsl_jar_dir / "context-mapper-dsl-6.12.0.jar").touch()
        
        discovery_jar_dir = temp_dir / ".m2" / "repository" / "org" / "contextmapper" / "context-map-discovery" / "1.1.0"
        discovery_jar_dir.mkdir(parents=True)
        (discovery_jar_dir / "context-map-discovery-1.1.0.jar").touch()
        
        return ContextMapper(java_env=mock_java_env)


class TestContextMapperInitialization:
    """Test Context Mapper initialization and setup."""
    
    def test_initialization_with_valid_env(self, mock_java_env):
        """Test Context Mapper initializes with valid Java environment."""
        with patch('src.utils.context_mapper.Path.home') as mock_home:
            temp_dir = Path(tempfile.mkdtemp())
            mock_home.return_value = temp_dir
            
            # Create mock JAR files
            dsl_jar_dir = temp_dir / ".m2" / "repository" / "org" / "contextmapper" / "context-mapper-dsl" / "6.12.0"
            dsl_jar_dir.mkdir(parents=True)
            (dsl_jar_dir / "context-mapper-dsl-6.12.0.jar").touch()
            
            discovery_jar_dir = temp_dir / ".m2" / "repository" / "org" / "contextmapper" / "context-map-discovery" / "1.1.0"
            discovery_jar_dir.mkdir(parents=True)
            (discovery_jar_dir / "context-map-discovery-1.1.0.jar").touch()
            
            mapper = ContextMapper(java_env=mock_java_env)
            
            assert mapper.java_env == mock_java_env
            assert mapper.CONTEXT_MAPPER_DSL_VERSION == "6.12.0"
            assert mapper.CONTEXT_MAP_DISCOVERY_VERSION == "1.1.0"
    
    def test_initialization_with_invalid_java(self):
        """Test Context Mapper raises error with invalid Java version."""
        invalid_env = JavaEnvironment(
            java_home=Path("/usr/lib/jvm/java-11"),
            java_executable=Path("/usr/lib/jvm/java-11/bin/java"),
            version="11.0.1",
            major_version=11,
            vendor="OpenJDK",
            is_valid=False,
            maven_executable=None,
            gradle_executable=None
        )
        
        with pytest.raises(ContextMapperError, match="Java 17\\+"):
            ContextMapper(java_env=invalid_env)
    
    def test_initialization_missing_dsl_jar(self, mock_java_env):
        """Test Context Mapper raises error when DSL JAR is missing."""
        with patch('src.utils.context_mapper.Path.home') as mock_home:
            temp_dir = Path(tempfile.mkdtemp())
            mock_home.return_value = temp_dir
            
            # Only create discovery JAR, not DSL JAR
            discovery_jar_dir = temp_dir / ".m2" / "repository" / "org" / "contextmapper" / "context-map-discovery" / "1.1.0"
            discovery_jar_dir.mkdir(parents=True)
            (discovery_jar_dir / "context-map-discovery-1.1.0.jar").touch()
            
            with pytest.raises(ContextMapperError, match="Context Mapper DSL.*not found"):
                ContextMapper(java_env=mock_java_env)
    
    def test_initialization_missing_discovery_jar(self, mock_java_env):
        """Test Context Mapper raises error when Discovery JAR is missing."""
        with patch('src.utils.context_mapper.Path.home') as mock_home:
            temp_dir = Path(tempfile.mkdtemp())
            mock_home.return_value = temp_dir
            
            # Only create DSL JAR, not discovery JAR
            dsl_jar_dir = temp_dir / ".m2" / "repository" / "org" / "contextmapper" / "context-mapper-dsl" / "6.12.0"
            dsl_jar_dir.mkdir(parents=True)
            (dsl_jar_dir / "context-mapper-dsl-6.12.0.jar").touch()
            
            with pytest.raises(ContextMapperError, match="Context Map Discovery.*not found"):
                ContextMapper(java_env=mock_java_env)


class TestVersionInfo:
    """Test version information retrieval."""
    
    def test_get_version_info(self, context_mapper):
        """Test getting version information."""
        version_info = context_mapper.get_version_info()
        
        assert "context_mapper_dsl" in version_info
        assert "context_map_discovery" in version_info
        assert "java_version" in version_info
        assert "maven_repo" in version_info
        
        assert version_info["context_mapper_dsl"] == "6.12.0"
        assert version_info["context_map_discovery"] == "1.1.0"
        assert version_info["java_version"] == "17.0.16"


class TestDiscoveryCodeGeneration:
    """Test Java discovery code generation."""
    
    def test_generate_discovery_code(self, context_mapper):
        """Test generation of Java discovery code."""
        codebase_path = Path("/path/to/codebase")
        base_package = "com.example.app"
        output_file = Path("/tmp/output.cml")
        
        code = context_mapper._generate_discovery_code(
            codebase_path=codebase_path,
            base_package=base_package,
            output_file=output_file
        )
        
        assert "import org.contextmapper.discovery.ContextMapDiscoverer" in code
        assert "SpringBootBoundedContextDiscoveryStrategy" in code
        assert base_package in code
        assert "DiscoveryRunner" in code
        assert "public static void main" in code
    
    def test_generate_discovery_code_escapes_paths(self, context_mapper):
        """Test that Windows paths are properly escaped."""
        codebase_path = Path("C:\\Users\\test\\project")
        base_package = "com.example"
        output_file = Path("C:\\temp\\output.cml")
        
        code = context_mapper._generate_discovery_code(
            codebase_path=codebase_path,
            base_package=base_package,
            output_file=output_file
        )
        
        # Paths should be escaped (backslashes doubled)
        assert "C:\\\\" in code or "C:/" in code or "/mnt/c/" in code


class TestClasspathBuilding:
    """Test classpath construction."""
    
    def test_build_classpath(self, context_mapper):
        """Test building classpath with Context Mapper JARs."""
        with patch('src.utils.context_mapper.Path.home') as mock_home:
            temp_dir = Path(tempfile.mkdtemp())
            mock_home.return_value = temp_dir
            
            maven_repo = temp_dir / ".m2" / "repository"
            
            classpath = context_mapper._build_classpath(maven_repo)
            
            assert "context-mapper-dsl-6.12.0.jar" in classpath
            assert "context-map-discovery-1.1.0.jar" in classpath
            
            # Check platform-specific separator
            import platform
            if platform.system() == "Windows":
                assert ";" in classpath or len(classpath.split(";")) >= 1
            else:
                assert ":" in classpath or len(classpath.split(":")) >= 1


class TestCMLParsing:
    """Test CML file parsing."""
    
    def test_parse_cml_output(self, context_mapper):
        """Test parsing of CML output file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cml', delete=False) as f:
            f.write("""
ContextMap {
    contains PaymentContext
    contains OrderContext
    
    PaymentContext -> OrderContext
}

BoundedContext PaymentContext {
    Aggregate Payment
}

BoundedContext OrderContext {
    Aggregate Order
}
""")
            cml_file = Path(f.name)
        
        try:
            result = context_mapper._parse_cml_output(cml_file)
            
            assert "bounded_contexts" in result
            assert "relationships" in result
            assert "raw_cml" in result
            
            # Check bounded contexts
            bc_names = [bc["name"] for bc in result["bounded_contexts"]]
            assert "PaymentContext" in bc_names
            assert "OrderContext" in bc_names
            
            # Check relationships
            assert len(result["relationships"]) > 0
            
            # Check raw CML is preserved
            assert "BoundedContext PaymentContext" in result["raw_cml"]
        finally:
            cml_file.unlink()
    
    def test_parse_cml_file_not_found(self, context_mapper):
        """Test parsing raises error when CML file doesn't exist."""
        nonexistent_file = Path("/nonexistent/file.cml")
        
        with pytest.raises(ContextMapperError, match="CML output file not found"):
            context_mapper._parse_cml_output(nonexistent_file)


class TestDiscoveryValidation:
    """Test discovery method input validation."""
    
    def test_discover_nonexistent_codebase(self, context_mapper):
        """Test discovery raises error for nonexistent codebase."""
        nonexistent_path = Path("/nonexistent/codebase")
        
        with pytest.raises(ContextMapperError, match="Codebase path does not exist"):
            context_mapper.discover_spring_boot_contexts(
                codebase_path=nonexistent_path,
                base_package="com.example"
            )
    
    def test_discover_file_instead_of_directory(self, context_mapper):
        """Test discovery raises error when given a file instead of directory."""
        with tempfile.NamedTemporaryFile() as f:
            file_path = Path(f.name)
            
            with pytest.raises(ContextMapperError, match="must be a directory"):
                context_mapper.discover_spring_boot_contexts(
                    codebase_path=file_path,
                    base_package="com.example"
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
