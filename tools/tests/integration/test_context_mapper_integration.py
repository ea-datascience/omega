"""
Integration Tests for Context Mapper

Tests the full integration with actual Context Mapper Java libraries.
These tests require:
- Java 17+
- Maven 3.9.9+
- Context Mapper libraries installed (via install-context-mapper.sh)
"""

import pytest
import tempfile
from pathlib import Path

from src.utils.context_mapper import ContextMapper, ContextMapperError


@pytest.fixture
def context_mapper():
    """Create real ContextMapper instance - requires Java and libraries installed."""
    try:
        return ContextMapper()
    except ContextMapperError as e:
        pytest.skip(f"Context Mapper not available: {e}")


class TestContextMapperIntegration:
    """Integration tests for Context Mapper with real Java libraries."""
    
    def test_context_mapper_available(self, context_mapper):
        """Test that Context Mapper is available and initialized."""
        assert context_mapper is not None
        assert context_mapper.java_env.is_valid
        assert context_mapper.java_env.major_version >= 17
    
    def test_get_version_info_integration(self, context_mapper):
        """Test getting version information from real installation."""
        version_info = context_mapper.get_version_info()
        
        assert version_info["context_mapper_dsl"] == "6.12.0"
        assert version_info["context_map_discovery"] == "1.1.0"
        assert "java_version" in version_info
        assert "maven_repo" in version_info
        
        # Verify actual JAR files exist
        maven_repo = Path(version_info["maven_repo"])
        
        dsl_jar = (
            maven_repo / "org" / "contextmapper" / "context-mapper-dsl" /
            "6.12.0" / "context-mapper-dsl-6.12.0.jar"
        )
        assert dsl_jar.exists(), f"DSL JAR not found at {dsl_jar}"
        
        discovery_jar = (
            maven_repo / "org" / "contextmapper" / "context-map-discovery" /
            "1.1.0" / "context-map-discovery-1.1.0.jar"
        )
        assert discovery_jar.exists(), f"Discovery JAR not found at {discovery_jar}"
    
    def test_classpath_building(self, context_mapper):
        """Test building valid classpath."""
        maven_repo = Path.home() / ".m2" / "repository"
        classpath = context_mapper._build_classpath(maven_repo)
        
        assert classpath is not None
        assert len(classpath) > 0
        assert "context-mapper-dsl" in classpath
        assert "context-map-discovery" in classpath
    
    def test_generate_discovery_code_syntax(self, context_mapper):
        """Test that generated Java code is syntactically valid."""
        code = context_mapper._generate_discovery_code(
            codebase_path=Path("/tmp/test"),
            base_package="com.test",
            output_file=Path("/tmp/output.cml")
        )
        
        # Basic syntax checks
        assert "import org.contextmapper" in code
        assert "public class DiscoveryRunner" in code
        assert "public static void main" in code
        assert "SpringBootBoundedContextDiscoveryStrategy" in code
        assert "com.test" in code
        
        # Verify proper Java structure
        assert code.count("{") == code.count("}")  # Balanced braces
        assert code.count("(") == code.count(")")  # Balanced parentheses


class TestContextMapperWithSampleCodebase:
    """Tests using a minimal sample Spring Boot codebase."""
    
    @pytest.fixture
    def sample_spring_boot_project(self):
        """Create a minimal Spring Boot project structure for testing."""
        temp_dir = Path(tempfile.mkdtemp(prefix="context-mapper-test-"))
        
        # Create minimal Spring Boot structure
        src_dir = temp_dir / "src" / "main" / "java" / "com" / "example" / "demo"
        src_dir.mkdir(parents=True)
        
        # Create a simple Spring Boot application class
        app_class = src_dir / "DemoApplication.java"
        app_class.write_text("""
package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
""")
        
        # Create a simple REST controller
        controller_dir = src_dir / "controller"
        controller_dir.mkdir()
        controller_class = controller_dir / "HelloController.java"
        controller_class.write_text("""
package com.example.demo.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {
    @GetMapping("/hello")
    public String hello() {
        return "Hello World";
    }
}
""")
        
        yield temp_dir
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_parse_cml_with_sample_output(self, context_mapper):
        """Test CML parsing with realistic sample output."""
        cml_content = """
ContextMap SampleSystem {
    contains DemoContext
}

BoundedContext DemoContext {
    implementationTechnology "Spring Boot"
    
    Aggregate HelloAggregate {
        Entity Hello {
            String message
        }
    }
}
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cml', delete=False) as f:
            f.write(cml_content)
            cml_file = Path(f.name)
        
        try:
            result = context_mapper._parse_cml_output(cml_file)
            
            assert "bounded_contexts" in result
            assert "relationships" in result
            assert "raw_cml" in result
            
            # Verify bounded context was found
            bc_names = [bc["name"] for bc in result["bounded_contexts"]]
            assert "DemoContext" in bc_names
            
            # Verify raw CML is preserved
            assert "implementationTechnology" in result["raw_cml"]
            assert "Spring Boot" in result["raw_cml"]
        finally:
            cml_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
