"""
Java Environment Utilities

Provides consistent Java setup, validation, and environment management
for all Omega project developers and analysis tools.

This module ensures:
- Java runtime detection and validation
- Version compatibility checking (Java 17+ required)
- JAVA_HOME management
- Classpath utilities
- Maven/Gradle detection
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class JavaEnvironment:
    """Represents detected Java environment configuration."""
    java_home: Optional[Path]
    java_executable: Path
    version: str
    major_version: int
    vendor: str
    is_valid: bool
    maven_executable: Optional[Path] = None
    gradle_executable: Optional[Path] = None


class JavaSetupError(Exception):
    """Raised when Java environment setup or validation fails."""
    pass


class JavaEnvironmentManager:
    """Manages Java environment detection, validation, and configuration."""
    
    MINIMUM_JAVA_VERSION = 17
    
    def __init__(self):
        self._cached_environment: Optional[JavaEnvironment] = None
    
    def detect_java_environment(self, force_refresh: bool = False) -> JavaEnvironment:
        """
        Detect and validate Java environment.
        
        Args:
            force_refresh: Force re-detection even if cached
            
        Returns:
            JavaEnvironment with detected configuration
            
        Raises:
            JavaSetupError: If Java cannot be detected or is invalid
        """
        if self._cached_environment and not force_refresh:
            return self._cached_environment
        
        java_home = self._detect_java_home()
        java_executable = self._find_java_executable(java_home)
        
        if not java_executable or not java_executable.exists():
            raise JavaSetupError(
                "Java executable not found. Please install Java 17+ or set JAVA_HOME."
            )
        
        version_info = self._get_java_version(java_executable)
        maven_exec = self._find_maven()
        gradle_exec = self._find_gradle()
        
        environment = JavaEnvironment(
            java_home=java_home,
            java_executable=java_executable,
            version=version_info["version"],
            major_version=version_info["major_version"],
            vendor=version_info["vendor"],
            is_valid=version_info["major_version"] >= self.MINIMUM_JAVA_VERSION,
            maven_executable=maven_exec,
            gradle_executable=gradle_exec
        )
        
        if not environment.is_valid:
            raise JavaSetupError(
                f"Java {self.MINIMUM_JAVA_VERSION}+ required. "
                f"Found Java {environment.major_version} ({environment.version})"
            )
        
        self._cached_environment = environment
        logger.info(
            f"Java environment detected: {environment.vendor} "
            f"{environment.version} at {environment.java_executable}"
        )
        
        return environment
    
    def _detect_java_home(self) -> Optional[Path]:
        """Detect JAVA_HOME from environment or common locations."""
        # Check JAVA_HOME environment variable
        java_home_env = os.environ.get("JAVA_HOME")
        if java_home_env:
            java_home = Path(java_home_env)
            if java_home.exists():
                return java_home
        
        # Try to detect from java executable location
        java_exec = shutil.which("java")
        if java_exec:
            java_path = Path(java_exec).resolve()
            # Navigate up from bin/java to JAVA_HOME
            if java_path.parent.name == "bin":
                potential_home = java_path.parent.parent
                if (potential_home / "bin" / "java").exists():
                    return potential_home
        
        return None
    
    def _find_java_executable(self, java_home: Optional[Path]) -> Optional[Path]:
        """Find java executable from JAVA_HOME or PATH."""
        # Try JAVA_HOME first
        if java_home:
            java_exec = java_home / "bin" / "java"
            if java_exec.exists():
                return java_exec
        
        # Fall back to PATH
        java_exec_str = shutil.which("java")
        if java_exec_str:
            return Path(java_exec_str)
        
        return None
    
    def _get_java_version(self, java_executable: Path) -> Dict[str, any]:
        """
        Extract Java version information from java -version output.
        
        Returns:
            Dict with version, major_version, and vendor
        """
        try:
            result = subprocess.run(
                [str(java_executable), "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Java outputs version to stderr
            version_output = result.stderr
            
            # Parse version string (handles both old and new formats)
            # Example: openjdk version "17.0.2" 2022-01-18
            # Example: java version "1.8.0_292"
            version_line = version_output.split('\n')[0]
            
            # Extract version number
            import re
            version_match = re.search(r'version "([^"]+)"', version_line)
            if not version_match:
                raise JavaSetupError(f"Could not parse Java version from: {version_line}")
            
            version_str = version_match.group(1)
            
            # Parse major version
            # Handle both "17.0.2" and "1.8.0_292" formats
            version_parts = version_str.split('.')
            if version_parts[0] == '1':
                # Old format: 1.8.0 means Java 8
                major_version = int(version_parts[1])
            else:
                # New format: 17.0.2 means Java 17
                major_version = int(version_parts[0])
            
            # Extract vendor
            vendor = "Unknown"
            if "openjdk" in version_output.lower():
                vendor = "OpenJDK"
            elif "oracle" in version_output.lower():
                vendor = "Oracle"
            elif "temurin" in version_output.lower():
                vendor = "Eclipse Temurin"
            elif "adoptium" in version_output.lower():
                vendor = "Eclipse Adoptium"
            
            return {
                "version": version_str,
                "major_version": major_version,
                "vendor": vendor
            }
            
        except subprocess.TimeoutExpired:
            raise JavaSetupError("Java version check timed out")
        except subprocess.SubprocessError as e:
            raise JavaSetupError(f"Failed to check Java version: {e}")
    
    def _find_maven(self) -> Optional[Path]:
        """Find Maven executable."""
        mvn = shutil.which("mvn")
        if mvn:
            return Path(mvn)
        
        # Check for mvnw (Maven Wrapper) in common locations
        for mvnw_name in ["mvnw", "mvnw.cmd"]:
            mvnw = shutil.which(mvnw_name)
            if mvnw:
                return Path(mvnw)
        
        return None
    
    def _find_gradle(self) -> Optional[Path]:
        """Find Gradle executable."""
        gradle = shutil.which("gradle")
        if gradle:
            return Path(gradle)
        
        # Check for gradlew (Gradle Wrapper) in common locations
        for gradlew_name in ["gradlew", "gradlew.bat"]:
            gradlew = shutil.which(gradlew_name)
            if gradlew:
                return Path(gradlew)
        
        return None
    
    def validate_environment(self) -> Tuple[bool, List[str]]:
        """
        Validate Java environment and return status with any issues.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        try:
            env = self.detect_java_environment()
            
            if not env.is_valid:
                issues.append(
                    f"Java {self.MINIMUM_JAVA_VERSION}+ required, "
                    f"found Java {env.major_version}"
                )
            
            if not env.maven_executable and not env.gradle_executable:
                issues.append(
                    "Neither Maven nor Gradle found. "
                    "At least one build tool is recommended for Java analysis."
                )
            
            return len(issues) == 0, issues
            
        except JavaSetupError as e:
            issues.append(str(e))
            return False, issues
    
    def get_java_command(self, args: List[str]) -> List[str]:
        """
        Get complete Java command with detected executable.
        
        Args:
            args: Java arguments (e.g., ['-jar', 'app.jar'])
            
        Returns:
            Complete command list for subprocess
        """
        env = self.detect_java_environment()
        return [str(env.java_executable)] + args
    
    def get_maven_command(self, goals: List[str]) -> List[str]:
        """
        Get complete Maven command with detected executable.
        
        Args:
            goals: Maven goals (e.g., ['clean', 'install'])
            
        Returns:
            Complete command list for subprocess
            
        Raises:
            JavaSetupError: If Maven is not available
        """
        env = self.detect_java_environment()
        if not env.maven_executable:
            raise JavaSetupError("Maven not found. Please install Maven or use Maven Wrapper (mvnw).")
        
        return [str(env.maven_executable)] + goals
    
    def get_gradle_command(self, tasks: List[str]) -> List[str]:
        """
        Get complete Gradle command with detected executable.
        
        Args:
            tasks: Gradle tasks (e.g., ['clean', 'build'])
            
        Returns:
            Complete command list for subprocess
            
        Raises:
            JavaSetupError: If Gradle is not available
        """
        env = self.detect_java_environment()
        if not env.gradle_executable:
            raise JavaSetupError("Gradle not found. Please install Gradle or use Gradle Wrapper (gradlew).")
        
        return [str(env.gradle_executable)] + tasks
    
    def setup_environment_variables(self) -> Dict[str, str]:
        """
        Get environment variables dict with Java configuration.
        
        Useful for subprocess calls that need JAVA_HOME set.
        
        Returns:
            Dict of environment variables including JAVA_HOME
        """
        env = self.detect_java_environment()
        env_vars = os.environ.copy()
        
        if env.java_home:
            env_vars["JAVA_HOME"] = str(env.java_home)
        
        return env_vars
    
    def print_environment_info(self) -> None:
        """Print detailed Java environment information for debugging."""
        try:
            env = self.detect_java_environment()
            
            print("=" * 60)
            print("Java Environment Information")
            print("=" * 60)
            print(f"Java Home:       {env.java_home or 'Not set'}")
            print(f"Java Executable: {env.java_executable}")
            print(f"Java Version:    {env.version}")
            print(f"Major Version:   {env.major_version}")
            print(f"Vendor:          {env.vendor}")
            print(f"Valid:           {env.is_valid}")
            print(f"Maven:           {env.maven_executable or 'Not found'}")
            print(f"Gradle:          {env.gradle_executable or 'Not found'}")
            print("=" * 60)
            
            is_valid, issues = self.validate_environment()
            if issues:
                print("\nIssues Found:")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print("\nEnvironment is valid and ready!")
                
        except JavaSetupError as e:
            print(f"Error detecting Java environment: {e}")


# Singleton instance for convenience
_java_env_manager = JavaEnvironmentManager()


def get_java_environment() -> JavaEnvironment:
    """
    Convenience function to get Java environment.
    
    Returns:
        JavaEnvironment with detected configuration
        
    Raises:
        JavaSetupError: If Java environment is invalid
    """
    return _java_env_manager.detect_java_environment()


def validate_java_setup() -> Tuple[bool, List[str]]:
    """
    Convenience function to validate Java setup.
    
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    return _java_env_manager.validate_environment()


def require_java() -> JavaEnvironment:
    """
    Require valid Java environment or raise exception.
    
    Use this at the start of functions that need Java.
    
    Returns:
        JavaEnvironment if valid
        
    Raises:
        JavaSetupError: If Java environment is invalid
    """
    env = get_java_environment()
    if not env.is_valid:
        raise JavaSetupError(
            f"Java {JavaEnvironmentManager.MINIMUM_JAVA_VERSION}+ required. "
            f"Found Java {env.major_version}"
        )
    return env


if __name__ == "__main__":
    # Command-line utility to check Java environment
    import sys
    
    try:
        manager = JavaEnvironmentManager()
        manager.print_environment_info()
        sys.exit(0)
    except JavaSetupError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
