"""
Context Mapper Integration Module

This module provides Python integration with Context Mapper Java libraries for
architectural analysis and context mapping in monolith-to-microservices migration.

Features:
- Context Map discovery from Spring Boot codebases
- Bounded Context identification
- Relationship mapping
- CML (Context Mapping Language) generation

Dependencies:
- context-mapper-dsl 6.12.0
- context-map-discovery 1.1.0
- Java 17+
- Maven 3.9.9+
"""

import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

from src.utils.java_utils import JavaEnvironment, JavaEnvironmentManager
from src.utils.spring_boot_analyzer import SpringBootAnalyzer, AnalysisResult

logger = logging.getLogger(__name__)


class ContextMapperError(Exception):
    """Base exception for Context Mapper operations"""
    pass


class ContextMapper:
    """
    Python wrapper for Context Mapper Java libraries.
    
    Provides high-level API for discovering bounded contexts and relationships
    from Spring Boot applications.
    
    Version Information:
    - context-mapper-dsl: 6.12.0
    - context-map-discovery: 1.1.0
    """
    
    CONTEXT_MAPPER_DSL_VERSION = "6.12.0"
    CONTEXT_MAP_DISCOVERY_VERSION = "1.1.0"
    
    def __init__(self, java_env: Optional[JavaEnvironment] = None):
        """
        Initialize Context Mapper integration.
        
        Args:
            java_env: JavaEnvironment instance. If None, detects automatically.
            
        Raises:
            ContextMapperError: If Java environment is not properly configured
        """
        if java_env is None:
            java_manager = JavaEnvironmentManager()
            try:
                self.java_env = java_manager.detect_java_environment()
            except Exception as e:
                raise ContextMapperError(
                    f"Failed to detect Java environment: {e}"
                )
        else:
            self.java_env = java_env
        
        if not self.java_env.is_valid:
            raise ContextMapperError(
                f"Java 17+ is required but found Java {self.java_env.major_version}. "
                "Please install Java 17 or later."
            )
        
        self._verify_context_mapper_installed()
    
    def _verify_context_mapper_installed(self) -> None:
        """
        Verify Context Mapper libraries are installed in Maven local repository.
        
        Raises:
            ContextMapperError: If Context Mapper is not installed
        """
        maven_repo = Path.home() / ".m2" / "repository"
        
        dsl_jar = (
            maven_repo / "org" / "contextmapper" / "context-mapper-dsl" /
            self.CONTEXT_MAPPER_DSL_VERSION / 
            f"context-mapper-dsl-{self.CONTEXT_MAPPER_DSL_VERSION}.jar"
        )
        
        discovery_jar = (
            maven_repo / "org" / "contextmapper" / "context-map-discovery" /
            self.CONTEXT_MAP_DISCOVERY_VERSION /
            f"context-map-discovery-{self.CONTEXT_MAP_DISCOVERY_VERSION}.jar"
        )
        
        if not dsl_jar.exists():
            raise ContextMapperError(
                f"Context Mapper DSL {self.CONTEXT_MAPPER_DSL_VERSION} not found. "
                f"Please run install-context-mapper.sh first. "
                f"Expected: {dsl_jar}"
            )
        
        if not discovery_jar.exists():
            raise ContextMapperError(
                f"Context Map Discovery {self.CONTEXT_MAP_DISCOVERY_VERSION} not found. "
                f"Please run install-context-mapper.sh first. "
                f"Expected: {discovery_jar}"
            )
        
        logger.info("Context Mapper libraries verified")
    
    def discover_spring_boot_contexts(
        self,
        codebase_path: Path,
        base_package: str,
        output_dir: Optional[Path] = None
    ) -> Dict:
        """
        Discover bounded contexts from a Spring Boot application.
        
        IMPORTANT: This method uses SpringBootBoundedContextDiscoveryStrategy which
        requires COMPILED CLASS FILES (.class). It scans bytecode using reflection
        to find @SpringBootApplication annotations. Source code (.java files) alone
        is NOT sufficient.
        
        Prerequisites:
        1. Project must be COMPILED (mvn compile, gradle build, etc.)
        2. codebase_path should point to project root OR compiled classes directory
        3. All dependencies must be available on classpath
        
        Args:
            codebase_path: Path to Spring Boot application root or compiled classes
            base_package: Base package name (e.g., "com.example.app")
            output_dir: Directory to write CML output. If None, uses temp directory.
            
        Returns:
            Dictionary containing discovered context map with structure:
            {
                "bounded_contexts": [...],  # List of discovered contexts
                "relationships": [...],     # List of context relationships
                "cml_file": "path/to/output.cml",
                "raw_cml": "CML content as string"
            }
            
            Note: bounded_contexts may be empty if:
            - No @SpringBootApplication annotations found
            - Project not compiled (only source code present)
            - Base package mismatch
            - Classpath issues
            
        Raises:
            ContextMapperError: If discovery fails or codebase path invalid
            
        Example:
            >>> mapper = ContextMapper()
            >>> # Ensure project is compiled first!
            >>> result = mapper.discover_spring_boot_contexts(
            ...     codebase_path=Path("/path/to/spring-boot-app"),
            ...     base_package="com.example.myapp"
            ... )
            >>> print(f"Found {len(result['bounded_contexts'])} contexts")
        """
        if not codebase_path.exists():
            raise ContextMapperError(f"Codebase path does not exist: {codebase_path}")
        
        if not codebase_path.is_dir():
            raise ContextMapperError(f"Codebase path must be a directory: {codebase_path}")
        
        output_dir = output_dir or Path(tempfile.mkdtemp(prefix="context-mapper-"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cml_output = output_dir / f"{codebase_path.name}_context_map.cml"
        
        logger.info(f"Discovering contexts in {codebase_path}")
        logger.info(f"Base package: {base_package}")
        logger.info(f"Output: {cml_output}")
        
        # Create Java runner to execute Context Mapper discovery
        java_code = self._generate_discovery_code(
            codebase_path=codebase_path,
            base_package=base_package,
            output_file=cml_output
        )
        
        # Execute discovery
        result = self._run_java_discovery(java_code)
        
        # Parse CML output
        context_map = self._parse_cml_output(cml_output)
        context_map["cml_file"] = str(cml_output)
        
        return context_map
    
    def _generate_discovery_code(
        self,
        codebase_path: Path,
        base_package: str,
        output_file: Path
    ) -> str:
        """
        Generate Java code for Context Mapper discovery.
        
        Args:
            codebase_path: Path to codebase
            base_package: Base package name
            output_file: Output CML file path
            
        Returns:
            Java source code as string
        """
        # Escape backslashes for Windows paths
        codebase_str = str(codebase_path.absolute()).replace("\\", "\\\\")
        output_str = str(output_file.absolute()).replace("\\", "\\\\")
        
        return f'''
import org.contextmapper.discovery.ContextMapDiscoverer;
import org.contextmapper.discovery.strategies.boundedcontexts.SpringBootBoundedContextDiscoveryStrategy;
import org.contextmapper.discovery.model.ContextMap;
import org.contextmapper.discovery.ContextMapSerializer;
import java.io.File;
import java.io.IOException;

public class DiscoveryRunner {{
    public static void main(String[] args) throws IOException {{
        ContextMapDiscoverer discoverer = new ContextMapDiscoverer()
            .usingBoundedContextDiscoveryStrategies(
                new SpringBootBoundedContextDiscoveryStrategy("{base_package}")
            );
        
        // Set source path
        System.setProperty("user.dir", "{codebase_str}");
        
        // Run discovery
        ContextMap contextMap = discoverer.discoverContextMap();
        
        // Serialize to CML (handle empty context maps)
        if (contextMap.getBoundedContexts().size() > 0) {{
            new ContextMapSerializer().serializeContextMap(
                contextMap,
                new File("{output_str}")
            );
            System.out.println("SUCCESS: Context map written to {output_str}");
        }} else {{
            // Create empty CML file for empty context maps
            java.io.PrintWriter writer = new java.io.PrintWriter("{output_str}", "UTF-8");
            writer.println("/* No bounded contexts discovered */");
            writer.println("/* This may indicate: */");
            writer.println("/*   - No Spring Boot applications in codebase */");
            writer.println("/*   - Base package mismatch */");
            writer.println("/*   - Source code location issue */");
            writer.close();
            System.out.println("INFO: No bounded contexts discovered - empty CML generated");
        }}
    }}
}}
'''
    
    def _run_java_discovery(self, java_code: str) -> str:
        """
        Compile and run Java discovery code.
        
        Args:
            java_code: Java source code to execute
            
        Returns:
            Output from Java execution
            
        Raises:
            ContextMapperError: If compilation or execution fails
        """
        with tempfile.TemporaryDirectory(prefix="context-mapper-java-") as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write Java source
            java_file = temp_path / "DiscoveryRunner.java"
            java_file.write_text(java_code)
            
            # Build classpath with Context Mapper JARs
            maven_repo = Path.home() / ".m2" / "repository"
            classpath = self._build_classpath(maven_repo)
            
            # Compile
            javac_path = self.java_env.java_home / "bin" / "javac" if self.java_env.java_home else Path("javac")
            compile_cmd = [
                str(javac_path),
                "-cp", classpath,
                str(java_file)
            ]
            
            logger.debug(f"Compile command: {' '.join(compile_cmd)}")
            
            try:
                result = subprocess.run(
                    compile_cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                raise ContextMapperError(
                    f"Java compilation failed:\n{e.stderr}"
                )
            
            # Run
            import platform
            separator = ":" if platform.system() != "Windows" else ";"
            run_cmd = [
                str(self.java_env.java_executable),
                "-cp", f"{temp_path}{separator}{classpath}",
                "DiscoveryRunner"
            ]
            
            logger.debug(f"Run command: {' '.join(run_cmd)}")
            
            try:
                result = subprocess.run(
                    run_cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout
            except subprocess.CalledProcessError as e:
                raise ContextMapperError(
                    f"Java execution failed:\n{e.stderr}"
                )
    
    def _build_classpath(self, maven_repo: Path) -> str:
        """
        Build classpath string with all Context Mapper dependencies.
        
        Args:
            maven_repo: Path to Maven local repository
            
        Returns:
            Classpath string with all required JARs
        """
        jars = []
        
        # Context Mapper core JARs
        jars.append(
            maven_repo / "org" / "contextmapper" / "context-mapper-dsl" /
            self.CONTEXT_MAPPER_DSL_VERSION /
            f"context-mapper-dsl-{self.CONTEXT_MAPPER_DSL_VERSION}.jar"
        )
        
        jars.append(
            maven_repo / "org" / "contextmapper" / "context-map-discovery" /
            self.CONTEXT_MAP_DISCOVERY_VERSION /
            f"context-map-discovery-{self.CONTEXT_MAP_DISCOVERY_VERSION}.jar"
        )
        
        # Collect all transitive dependencies from Maven repository
        # These were downloaded by install-context-mapper.sh
        dependency_patterns = [
            "org/springframework/**/*.jar",
            "org/reflections/**/*.jar",
            "com/google/guava/**/*.jar",
            "org/javassist/**/*.jar",
            "org/eclipse/**/*.jar",
            "org/freemarker/**/*.jar",
            "org/yaml/**/*.jar",
            "com/fasterxml/jackson/**/*.jar",
            "org/slf4j/**/*.jar",
            "ch/qos/**/*.jar",
            "org/antlr/**/*.jar",
            "org/apache/commons/**/*.jar",
            "commons-io/**/*.jar",
            "io/github/classgraph/**/*.jar",
            "org/ow2/asm/**/*.jar",
            "com/google/inject/**/*.jar",
            "jakarta/inject/**/*.jar",
            "aopalliance/**/*.jar",
        ]
        
        for pattern in dependency_patterns:
            for jar in maven_repo.glob(pattern):
                if jar.is_file() and jar.suffix == ".jar":
                    jars.append(jar)
        
        import platform
        separator = ":" if platform.system() != "Windows" else ";"
        return separator.join(str(jar) for jar in jars)
    
    def _parse_cml_output(self, cml_file: Path) -> Dict:
        """
        Parse CML file and extract bounded contexts and relationships.
        
        Args:
            cml_file: Path to CML file
            
        Returns:
            Dictionary with parsed context map
        """
        if not cml_file.exists():
            raise ContextMapperError(f"CML output file not found: {cml_file}")
        
        cml_content = cml_file.read_text()
        
        # Simple CML parser - extracts basic structure
        # TODO: Implement full CML parser or use Context Mapper's API
        bounded_contexts = []
        relationships = []
        
        # Extract bounded context names
        import re
        bc_pattern = r'BoundedContext\s+(\w+)'
        for match in re.finditer(bc_pattern, cml_content):
            bounded_contexts.append({
                "name": match.group(1),
                "type": "discovered"
            })
        
        # Extract relationships
        rel_pattern = r'(\w+)\s*->\s*(\w+)'
        for match in re.finditer(rel_pattern, cml_content):
            relationships.append({
                "from": match.group(1),
                "to": match.group(2),
                "type": "dependency"
            })
        
        return {
            "bounded_contexts": bounded_contexts,
            "relationships": relationships,
            "raw_cml": cml_content
        }
    
    def get_version_info(self) -> Dict[str, str]:
        """
        Get version information for Context Mapper components.
        
        Returns:
            Dictionary with component versions
        """
        return {
            "context_mapper_dsl": self.CONTEXT_MAPPER_DSL_VERSION,
            "context_map_discovery": self.CONTEXT_MAP_DISCOVERY_VERSION,
            "java_version": self.java_env.version,
            "maven_repo": str(Path.home() / ".m2" / "repository")
        }
    
    def analyze_spring_boot_source(
        self,
        project_path: Path,
        base_package: str,
        output_dir: Optional[Path] = None
    ) -> Dict:
        """
        Analyze Spring Boot project from source code (no compilation required).
        
        This method uses SpringBootAnalyzer to read Java source files directly,
        unlike discover_spring_boot_contexts() which requires compiled classes.
        
        Recommended for:
        - Quick analysis without compilation
        - Projects that are difficult to compile
        - Source-only analysis
        
        Args:
            project_path: Path to Spring Boot project root
            base_package: Base Java package (e.g., "com.example.app")
            output_dir: Directory to write outputs. If None, uses temp directory.
            
        Returns:
            Dictionary containing:
            {
                "application": "ApplicationClass",
                "base_package": "com.example.app",
                "modules": [...],
                "dependencies": [...],
                "cml_file": "path/to/output.cml",
                "json_file": "path/to/output.json",
                "raw_cml": "CML content"
            }
            
        Raises:
            ContextMapperError: If analysis fails
            
        Example:
            >>> mapper = ContextMapper()
            >>> result = mapper.analyze_spring_boot_source(
            ...     project_path=Path("/path/to/spring-boot-app"),
            ...     base_package="com.example.app"
            ... )
            >>> print(f"Found {len(result['modules'])} modules")
        """
        if not project_path.exists():
            raise ContextMapperError(
                f"Project path does not exist: {project_path}"
            )
        
        output_dir = output_dir or Path(tempfile.mkdtemp(prefix="context-mapper-"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Analyzing Spring Boot source code: {project_path}")
        
        # Use SpringBootAnalyzer for source code analysis
        analyzer = SpringBootAnalyzer()
        
        try:
            analysis = analyzer.analyze_project(project_path, base_package)
        except Exception as e:
            raise ContextMapperError(f"Source code analysis failed: {e}")
        
        # Generate outputs
        project_name = project_path.name
        cml_file = output_dir / f"{project_name}_context_map.cml"
        json_file = output_dir / f"{project_name}_analysis.json"
        
        # Generate CML
        cml_content = analyzer.generate_cml(analysis, cml_file)
        
        # Generate JSON
        analyzer.generate_json_report(analysis, json_file)
        
        logger.info(f"Analysis complete. CML: {cml_file}, JSON: {json_file}")
        
        # Return unified result format
        return {
            "application": analysis.application_class,
            "base_package": analysis.base_package,
            "modules": [m.to_dict() for m in analysis.modules],
            "dependencies": [d.to_dict() for d in analysis.dependencies],
            "cml_file": str(cml_file),
            "json_file": str(json_file),
            "raw_cml": cml_content
        }


def main():
    """Command-line interface for Context Mapper."""
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    try:
        mapper = ContextMapper()
        version_info = mapper.get_version_info()
        
        print("Context Mapper Integration")
        print("=" * 60)
        print(f"Context Mapper DSL: {version_info['context_mapper_dsl']}")
        print(f"Context Map Discovery: {version_info['context_map_discovery']}")
        print(f"Java Version: {version_info['java_version']}")
        print(f"Maven Repository: {version_info['maven_repo']}")
        print("=" * 60)
        print("\nContext Mapper is ready to use!")
        
        sys.exit(0)
    except ContextMapperError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
