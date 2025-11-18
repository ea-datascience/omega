"""
Unit Tests for Java Utilities

Tests for Java environment detection, validation, and management.
"""

import pytest
import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

from utils.java_utils import (
    JavaEnvironment,
    JavaEnvironmentManager,
    JavaSetupError,
    get_java_environment,
    validate_java_setup,
    require_java
)


class TestJavaEnvironmentManager:
    """Test JavaEnvironmentManager functionality."""
    
    def test_detect_java_environment_success(self):
        """Test successful Java environment detection."""
        manager = JavaEnvironmentManager()
        
        # This should work in the dev container
        env = manager.detect_java_environment()
        
        assert env is not None
        assert env.java_executable is not None
        assert env.java_executable.exists()
        assert env.major_version >= 17
        assert env.is_valid is True
        assert env.version is not None
        assert env.vendor is not None
    
    def test_detect_java_environment_caching(self):
        """Test that environment detection is cached."""
        manager = JavaEnvironmentManager()
        
        env1 = manager.detect_java_environment()
        env2 = manager.detect_java_environment(force_refresh=False)
        
        # Should return same instance
        assert env1 is env2
    
    def test_detect_java_environment_force_refresh(self):
        """Test force refresh bypasses cache."""
        manager = JavaEnvironmentManager()
        
        env1 = manager.detect_java_environment()
        manager._cached_environment = None  # Clear cache
        env2 = manager.detect_java_environment(force_refresh=True)
        
        # Should detect again (same values but different instance)
        assert env1.java_executable == env2.java_executable
    
    def test_minimum_version_check(self):
        """Test that minimum Java version is enforced."""
        manager = JavaEnvironmentManager()
        env = manager.detect_java_environment()
        
        # Dev container has Java 17+
        assert env.major_version >= JavaEnvironmentManager.MINIMUM_JAVA_VERSION
        assert env.is_valid is True
    
    def test_validate_environment_success(self):
        """Test environment validation with valid setup."""
        manager = JavaEnvironmentManager()
        is_valid, issues = manager.validate_environment()
        
        # Should be valid in dev container (Maven/Gradle warning is acceptable)
        # Java is valid even without build tools
        if not is_valid:
            assert all("Maven" in issue or "Gradle" in issue for issue in issues)
        else:
            assert is_valid is True
    
    def test_get_java_command(self):
        """Test Java command generation."""
        manager = JavaEnvironmentManager()
        
        cmd = manager.get_java_command(['-version'])
        
        assert len(cmd) == 2
        assert cmd[0].endswith('java') or cmd[0].endswith('java.exe')
        assert cmd[1] == '-version'
    
    def test_get_java_command_with_multiple_args(self):
        """Test Java command with multiple arguments."""
        manager = JavaEnvironmentManager()
        
        cmd = manager.get_java_command(['-jar', 'app.jar', '--spring.profiles.active=prod'])
        
        assert len(cmd) == 4
        assert cmd[1] == '-jar'
        assert cmd[2] == 'app.jar'
        assert cmd[3] == '--spring.profiles.active=prod'
    
    def test_setup_environment_variables(self):
        """Test environment variables setup."""
        manager = JavaEnvironmentManager()
        
        env_vars = manager.setup_environment_variables()
        
        # Should have JAVA_HOME if detected
        env = manager.detect_java_environment()
        if env.java_home:
            assert 'JAVA_HOME' in env_vars
            assert env_vars['JAVA_HOME'] == str(env.java_home)
    
    @patch('subprocess.run')
    def test_get_java_version_parsing_new_format(self, mock_run):
        """Test Java version parsing for new format (Java 9+)."""
        mock_run.return_value = MagicMock(
            stderr='openjdk version "17.0.2" 2022-01-18\n'
                   'OpenJDK Runtime Environment (build 17.0.2+8-86)\n'
        )
        
        manager = JavaEnvironmentManager()
        java_exec = Path('/usr/bin/java')
        
        version_info = manager._get_java_version(java_exec)
        
        assert version_info['version'] == '17.0.2'
        assert version_info['major_version'] == 17
        assert version_info['vendor'] == 'OpenJDK'
    
    @patch('subprocess.run')
    def test_get_java_version_parsing_old_format(self, mock_run):
        """Test Java version parsing for old format (Java 8)."""
        mock_run.return_value = MagicMock(
            stderr='java version "1.8.0_292"\n'
                   'Java(TM) SE Runtime Environment (build 1.8.0_292-b10)\n'
        )
        
        manager = JavaEnvironmentManager()
        java_exec = Path('/usr/bin/java')
        
        version_info = manager._get_java_version(java_exec)
        
        assert version_info['version'] == '1.8.0_292'
        assert version_info['major_version'] == 8
    
    @patch('subprocess.run')
    def test_get_java_version_timeout(self, mock_run):
        """Test Java version check with timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired('java', 5)
        
        manager = JavaEnvironmentManager()
        java_exec = Path('/usr/bin/java')
        
        with pytest.raises(JavaSetupError, match="timed out"):
            manager._get_java_version(java_exec)
    
    @patch('shutil.which')
    def test_find_maven_not_found(self, mock_which):
        """Test Maven detection when not available."""
        mock_which.return_value = None
        
        manager = JavaEnvironmentManager()
        maven_exec = manager._find_maven()
        
        assert maven_exec is None
    
    @patch('shutil.which')
    def test_find_maven_found(self, mock_which):
        """Test Maven detection when available."""
        mock_which.return_value = '/usr/bin/mvn'
        
        manager = JavaEnvironmentManager()
        maven_exec = manager._find_maven()
        
        assert maven_exec == Path('/usr/bin/mvn')
    
    @patch('shutil.which')
    def test_find_gradle_not_found(self, mock_which):
        """Test Gradle detection when not available."""
        mock_which.return_value = None
        
        manager = JavaEnvironmentManager()
        gradle_exec = manager._find_gradle()
        
        assert gradle_exec is None
    
    @patch('shutil.which')
    def test_find_gradle_found(self, mock_which):
        """Test Gradle detection when available."""
        mock_which.return_value = '/usr/bin/gradle'
        
        manager = JavaEnvironmentManager()
        gradle_exec = manager._find_gradle()
        
        assert gradle_exec == Path('/usr/bin/gradle')


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_get_java_environment(self):
        """Test get_java_environment convenience function."""
        env = get_java_environment()
        
        assert env is not None
        assert env.is_valid is True
    
    def test_validate_java_setup(self):
        """Test validate_java_setup convenience function."""
        is_valid, issues = validate_java_setup()
        
        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)
    
    def test_require_java_success(self):
        """Test require_java with valid environment."""
        env = require_java()
        
        assert env is not None
        assert env.is_valid is True
    
    @patch('utils.java_utils._java_env_manager')
    def test_require_java_failure(self, mock_manager):
        """Test require_java with invalid environment."""
        mock_env = JavaEnvironment(
            java_home=None,
            java_executable=Path('/usr/bin/java'),
            version='11.0.0',
            major_version=11,
            vendor='OpenJDK',
            is_valid=False
        )
        mock_manager.detect_java_environment.return_value = mock_env
        
        with pytest.raises(JavaSetupError, match="Java 17\\+ required"):
            require_java()


class TestJavaEnvironmentDataclass:
    """Test JavaEnvironment dataclass."""
    
    def test_java_environment_creation(self):
        """Test creating JavaEnvironment instance."""
        env = JavaEnvironment(
            java_home=Path('/usr/local/java'),
            java_executable=Path('/usr/local/java/bin/java'),
            version='17.0.2',
            major_version=17,
            vendor='OpenJDK',
            is_valid=True
        )
        
        assert env.java_home == Path('/usr/local/java')
        assert env.java_executable == Path('/usr/local/java/bin/java')
        assert env.version == '17.0.2'
        assert env.major_version == 17
        assert env.vendor == 'OpenJDK'
        assert env.is_valid is True
        assert env.maven_executable is None
        assert env.gradle_executable is None
    
    def test_java_environment_with_build_tools(self):
        """Test JavaEnvironment with Maven and Gradle."""
        env = JavaEnvironment(
            java_home=Path('/usr/local/java'),
            java_executable=Path('/usr/local/java/bin/java'),
            version='17.0.2',
            major_version=17,
            vendor='OpenJDK',
            is_valid=True,
            maven_executable=Path('/usr/bin/mvn'),
            gradle_executable=Path('/usr/bin/gradle')
        )
        
        assert env.maven_executable == Path('/usr/bin/mvn')
        assert env.gradle_executable == Path('/usr/bin/gradle')


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @patch('shutil.which')
    @patch.dict(os.environ, {}, clear=True)
    def test_java_not_found(self, mock_which):
        """Test behavior when Java is not found."""
        mock_which.return_value = None
        
        manager = JavaEnvironmentManager()
        manager._cached_environment = None  # Clear cache
        
        with pytest.raises(JavaSetupError, match="Java executable not found"):
            manager.detect_java_environment()
    
    @patch('utils.java_utils.JavaEnvironmentManager.detect_java_environment')
    def test_get_maven_command_not_available(self, mock_detect):
        """Test get_maven_command when Maven is not available."""
        mock_detect.return_value = JavaEnvironment(
            java_home=Path('/usr/local/java'),
            java_executable=Path('/usr/local/java/bin/java'),
            version='17.0.2',
            major_version=17,
            vendor='OpenJDK',
            is_valid=True,
            maven_executable=None
        )
        
        manager = JavaEnvironmentManager()
        
        with pytest.raises(JavaSetupError, match="Maven not found"):
            manager.get_maven_command(['clean', 'install'])
    
    @patch('utils.java_utils.JavaEnvironmentManager.detect_java_environment')
    def test_get_gradle_command_not_available(self, mock_detect):
        """Test get_gradle_command when Gradle is not available."""
        mock_detect.return_value = JavaEnvironment(
            java_home=Path('/usr/local/java'),
            java_executable=Path('/usr/local/java/bin/java'),
            version='17.0.2',
            major_version=17,
            vendor='OpenJDK',
            is_valid=True,
            gradle_executable=None
        )
        
        manager = JavaEnvironmentManager()
        
        with pytest.raises(JavaSetupError, match="Gradle not found"):
            manager.get_gradle_command(['build'])


class TestIntegrationWithRealEnvironment:
    """Integration tests with real Java environment."""
    
    def test_real_java_version_command(self):
        """Test actual java -version command."""
        manager = JavaEnvironmentManager()
        env = manager.detect_java_environment()
        
        # Run actual java -version command
        result = subprocess.run(
            [str(env.java_executable), '-version'],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert 'version' in result.stderr.lower()
    
    def test_real_environment_variables(self):
        """Test environment variables with real setup."""
        manager = JavaEnvironmentManager()
        env_vars = manager.setup_environment_variables()
        
        # Should include all current environment variables
        assert 'PATH' in env_vars
        
        # May have JAVA_HOME if detected
        env = manager.detect_java_environment()
        if env.java_home:
            assert env_vars.get('JAVA_HOME') == str(env.java_home)
    
    def test_print_environment_info_no_crash(self):
        """Test print_environment_info doesn't crash."""
        manager = JavaEnvironmentManager()
        
        # Should not raise exception
        try:
            manager.print_environment_info()
            assert True
        except Exception as e:
            pytest.fail(f"print_environment_info raised exception: {e}")
