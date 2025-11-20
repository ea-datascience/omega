"""
Unit tests for Structurizr CLI integration module.

These tests verify the Python wrapper API without requiring
actual Structurizr CLI execution.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess

from src.utils.structurizr_cli import (
    StructurizrCLI,
    StructurizrError,
    ExportResult,
    ValidationResult
)
from src.utils.java_utils import JavaEnvironment


class TestStructurizrCLI:
    """Test StructurizrCLI initialization and configuration"""
    
    @patch('src.utils.structurizr_cli.Path.exists')
    @patch('src.utils.structurizr_cli.JavaEnvironmentManager')
    def test_initialization_success(self, mock_java_manager, mock_exists):
        """Test successful CLI initialization"""
        mock_exists.return_value = True
        
        mock_java_env = JavaEnvironment(
            java_home="/usr/lib/jvm/java-17",
            java_executable="/usr/lib/jvm/java-17/bin/java",
            version="17.0.16",
            major_version=17,
            vendor="OpenJDK",
            is_valid=True
        )
        mock_java_manager.return_value.detect_java_environment.return_value = mock_java_env
        
        cli = StructurizrCLI()
        
        assert cli.cli_path == Path("/opt/structurizr-cli/structurizr.sh")
        assert cli.java_env.major_version == 17
    
    @patch('src.utils.structurizr_cli.Path.exists')
    def test_initialization_cli_not_found(self, mock_exists):
        """Test initialization failure when CLI not found"""
        mock_exists.return_value = False
        
        with pytest.raises(StructurizrError) as exc_info:
            StructurizrCLI()
        
        assert "Structurizr CLI not found" in str(exc_info.value)
    
    @patch('src.utils.structurizr_cli.Path.exists')
    @patch('src.utils.structurizr_cli.JavaEnvironmentManager')
    def test_initialization_java_too_old(self, mock_java_manager, mock_exists):
        """Test initialization failure with old Java version"""
        mock_exists.return_value = True
        
        mock_java_env = JavaEnvironment(
            java_home="/usr/lib/jvm/java-11",
            java_executable="/usr/lib/jvm/java-11/bin/java",
            version="11.0.1",
            major_version=11,
            vendor="OpenJDK",
            is_valid=False
        )
        mock_java_manager.return_value.detect_java_environment.return_value = mock_java_env
        
        with pytest.raises(StructurizrError) as exc_info:
            StructurizrCLI()
        
        assert "Java 17+ is required" in str(exc_info.value)
    
    @patch('src.utils.structurizr_cli.Path.exists')
    @patch('src.utils.structurizr_cli.JavaEnvironmentManager')
    def test_custom_cli_path(self, mock_java_manager, mock_exists):
        """Test initialization with custom CLI path"""
        mock_exists.return_value = True
        
        mock_java_env = JavaEnvironment(
            java_home="/usr/lib/jvm/java-17",
            java_executable="/usr/lib/jvm/java-17/bin/java",
            version="17.0.16",
            major_version=17,
            vendor="OpenJDK",
            is_valid=True
        )
        mock_java_manager.return_value.detect_java_environment.return_value = mock_java_env
        
        custom_path = Path("/custom/structurizr.sh")
        cli = StructurizrCLI(cli_path=custom_path)
        
        assert cli.cli_path == custom_path


class TestExportDiagrams:
    """Test diagram export functionality"""
    
    @patch('src.utils.structurizr_cli.Path.exists')
    @patch('src.utils.structurizr_cli.subprocess.run')
    @patch('src.utils.structurizr_cli.JavaEnvironmentManager')
    def test_export_success_plantuml(self, mock_java_manager, mock_run, mock_exists):
        """Test successful PlantUML export"""
        mock_exists.return_value = True
        
        mock_java_env = JavaEnvironment(
            java_home="/usr/lib/jvm/java-17",
            java_executable="/usr/lib/jvm/java-17/bin/java",
            version="17.0.16",
            major_version=17,
            vendor="OpenJDK",
            is_valid=True
        )
        mock_java_manager.return_value.detect_java_environment.return_value = mock_java_env
        
        mock_run.return_value = Mock(returncode=0, stdout="Export successful", stderr="")
        
        cli = StructurizrCLI()
        
        workspace = Path("/tmp/workspace.dsl")
        output_dir = Path("/tmp/output")
        
        with patch.object(Path, 'glob', return_value=[Path("/tmp/output/diagram1.puml")]):
            result = cli.export_diagrams(
                workspace_file=workspace,
                format="plantuml",
                output_dir=output_dir
            )
        
        assert result.success
        assert result.format == "plantuml"
        assert len(result.files) == 1
    
    @patch('src.utils.structurizr_cli.Path.exists')
    @patch('src.utils.structurizr_cli.subprocess.run')
    @patch('src.utils.structurizr_cli.JavaEnvironmentManager')
    def test_export_failure(self, mock_java_manager, mock_run, mock_exists):
        """Test export failure handling"""
        mock_exists.return_value = True
        
        mock_java_env = JavaEnvironment(
            java_home="/usr/lib/jvm/java-17",
            java_executable="/usr/lib/jvm/java-17/bin/java",
            version="17.0.16",
            major_version=17,
            vendor="OpenJDK",
            is_valid=True
        )
        mock_java_manager.return_value.detect_java_environment.return_value = mock_java_env
        
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "cmd", stderr="Validation error"
        )
        
        cli = StructurizrCLI()
        
        workspace = Path("/tmp/workspace.dsl")
        result = cli.export_diagrams(
            workspace_file=workspace,
            format="mermaid",
            output_dir=Path("/tmp/output")
        )
        
        assert not result.success
        assert "Export failed" in result.message
    
    @patch('src.utils.structurizr_cli.Path.exists')
    @patch('src.utils.structurizr_cli.JavaEnvironmentManager')
    def test_export_workspace_not_found(self, mock_java_manager, mock_exists):
        """Test export with non-existent workspace file"""
        # Mock CLI exists but workspace doesn't
        def exists_side_effect():
            # Return True only for CLI path check
            return False
        
        # First call (CLI exists) returns True, subsequent calls return False
        mock_exists.side_effect = [True, False]
        
        mock_java_env = JavaEnvironment(
            java_home="/usr/lib/jvm/java-17",
            java_executable="/usr/lib/jvm/java-17/bin/java",
            version="17.0.16",
            major_version=17,
            vendor="OpenJDK",
            is_valid=True
        )
        mock_java_manager.return_value.detect_java_environment.return_value = mock_java_env
        
        cli = StructurizrCLI()
        
        with pytest.raises(StructurizrError) as exc_info:
            cli.export_diagrams(
                workspace_file=Path("/nonexistent/workspace.dsl"),
                format="plantuml",
                output_dir=Path("/tmp/output")
            )
        
        assert "Workspace file not found" in str(exc_info.value)


class TestValidateWorkspace:
    """Test workspace validation functionality"""
    
    @patch('src.utils.structurizr_cli.Path.exists')
    @patch('src.utils.structurizr_cli.subprocess.run')
    @patch('src.utils.structurizr_cli.JavaEnvironmentManager')
    def test_validate_success(self, mock_java_manager, mock_run, mock_exists):
        """Test successful workspace validation"""
        mock_exists.return_value = True
        
        mock_java_env = JavaEnvironment(
            java_home="/usr/lib/jvm/java-17",
            java_executable="/usr/lib/jvm/java-17/bin/java",
            version="17.0.16",
            major_version=17,
            vendor="OpenJDK",
            is_valid=True
        )
        mock_java_manager.return_value.detect_java_environment.return_value = mock_java_env
        
        mock_run.return_value = Mock(returncode=0, stdout="Workspace is valid", stderr="")
        
        cli = StructurizrCLI()
        
        workspace = Path("/tmp/workspace.dsl")
        result = cli.validate_workspace(workspace)
        
        assert result.valid
        assert len(result.errors) == 0
    
    @patch('src.utils.structurizr_cli.Path.exists')
    @patch('src.utils.structurizr_cli.subprocess.run')
    @patch('src.utils.structurizr_cli.JavaEnvironmentManager')
    def test_validate_failure(self, mock_java_manager, mock_run, mock_exists):
        """Test workspace validation failure"""
        mock_exists.return_value = True
        
        mock_java_env = JavaEnvironment(
            java_home="/usr/lib/jvm/java-17",
            java_executable="/usr/lib/jvm/java-17/bin/java",
            version="17.0.16",
            major_version=17,
            vendor="OpenJDK",
            is_valid=True
        )
        mock_java_manager.return_value.detect_java_environment.return_value = mock_java_env
        
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "cmd", stderr="Error: Unknown element 'badElement'\nError: Invalid syntax"
        )
        
        cli = StructurizrCLI()
        
        workspace = Path("/tmp/workspace.dsl")
        result = cli.validate_workspace(workspace)
        
        assert not result.valid
        assert len(result.errors) == 2


class TestInspectWorkspace:
    """Test workspace inspection functionality"""
    
    @patch('src.utils.structurizr_cli.Path.exists')
    @patch('src.utils.structurizr_cli.subprocess.run')
    @patch('src.utils.structurizr_cli.JavaEnvironmentManager')
    def test_inspect_success(self, mock_java_manager, mock_run, mock_exists):
        """Test successful workspace inspection"""
        mock_exists.return_value = True
        
        mock_java_env = JavaEnvironment(
            java_home="/usr/lib/jvm/java-17",
            java_executable="/usr/lib/jvm/java-17/bin/java",
            version="17.0.16",
            major_version=17,
            vendor="OpenJDK",
            is_valid=True
        )
        mock_java_manager.return_value.detect_java_environment.return_value = mock_java_env
        
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Model: 10 elements, 5 relationships",
            stderr=""
        )
        
        cli = StructurizrCLI()
        
        workspace = Path("/tmp/workspace.dsl")
        result = cli.inspect_workspace(workspace)
        
        assert result["success"]
        assert "10 elements" in result["output"]


class TestListElements:
    """Test element listing functionality"""
    
    @patch('src.utils.structurizr_cli.Path.exists')
    @patch('src.utils.structurizr_cli.subprocess.run')
    @patch('src.utils.structurizr_cli.JavaEnvironmentManager')
    def test_list_elements_success(self, mock_java_manager, mock_run, mock_exists):
        """Test successful element listing"""
        mock_exists.return_value = True
        
        mock_java_env = JavaEnvironment(
            java_home="/usr/lib/jvm/java-17",
            java_executable="/usr/lib/jvm/java-17/bin/java",
            version="17.0.16",
            major_version=17,
            vendor="OpenJDK",
            is_valid=True
        )
        mock_java_manager.return_value.detect_java_environment.return_value = mock_java_env
        
        mock_run.return_value = Mock(
            returncode=0,
            stdout="user\norder\ninventory\n",
            stderr=""
        )
        
        cli = StructurizrCLI()
        
        workspace = Path("/tmp/workspace.dsl")
        elements = cli.list_elements(workspace)
        
        assert len(elements) == 3
        assert "user" in elements
        assert "order" in elements


class TestVersionInfo:
    """Test version information retrieval"""
    
    @patch('src.utils.structurizr_cli.Path.exists')
    @patch('src.utils.structurizr_cli.JavaEnvironmentManager')
    def test_get_version_info(self, mock_java_manager, mock_exists):
        """Test version information retrieval"""
        mock_exists.return_value = True
        
        mock_java_env = JavaEnvironment(
            java_home="/usr/lib/jvm/java-17",
            java_executable="/usr/lib/jvm/java-17/bin/java",
            version="17.0.16",
            major_version=17,
            vendor="OpenJDK",
            is_valid=True
        )
        mock_java_manager.return_value.detect_java_environment.return_value = mock_java_env
        
        cli = StructurizrCLI()
        info = cli.get_version_info()
        
        assert info["structurizr_cli"] == "2025.11.09"
        assert info["java_version"] == "17.0.16"
        assert "structurizr.sh" in info["cli_path"]


class TestResultObjects:
    """Test result data classes"""
    
    def test_export_result_to_dict(self):
        """Test ExportResult serialization"""
        result = ExportResult(
            format="plantuml",
            output_dir=Path("/tmp/out"),
            files=[Path("/tmp/out/diagram.puml")],
            success=True,
            message="Success"
        )
        
        data = result.to_dict()
        
        assert data["format"] == "plantuml"
        assert data["success"] is True
        assert len(data["files"]) == 1
    
    def test_validation_result_to_dict(self):
        """Test ValidationResult serialization"""
        result = ValidationResult(
            valid=True,
            workspace_file=Path("/tmp/workspace.dsl"),
            message="Valid",
            errors=[]
        )
        
        data = result.to_dict()
        
        assert data["valid"] is True
        assert len(data["errors"]) == 0
