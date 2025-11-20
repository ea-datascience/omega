"""
Integration tests for Structurizr CLI module.

These tests verify the actual CLI integration with real
Structurizr workspace files and diagram export.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.utils.structurizr_cli import StructurizrCLI, StructurizrError


class TestStructurizrCLIIntegration:
    """Integration tests using real Structurizr CLI"""
    
    @pytest.fixture
    def cli(self):
        """Create StructurizrCLI instance"""
        try:
            return StructurizrCLI()
        except StructurizrError:
            pytest.skip("Structurizr CLI not installed")
    
    @pytest.fixture
    def sample_workspace(self, tmp_path):
        """Create a minimal test workspace DSL"""
        workspace_file = tmp_path / "workspace.dsl"
        
        workspace_content = """
workspace "Sample System" "A sample workspace for testing" {
    
    model {
        user = person "User" "A user of the system"
        softwareSystem = softwareSystem "Software System" "My software system" {
            webapp = container "Web Application" "Delivers content" "Java and Spring Boot" {
                tags "Application"
            }
            database = container "Database" "Stores information" "PostgreSQL" {
                tags "Database"
            }
        }
        
        user -> webapp "Uses"
        webapp -> database "Reads from and writes to" "JDBC"
    }
    
    views {
        systemContext softwareSystem "SystemContext" {
            include *
            autolayout lr
        }
        
        container softwareSystem "Containers" {
            include *
            autolayout lr
        }
        
        theme default
    }
}
"""
        workspace_file.write_text(workspace_content)
        return workspace_file
    
    @pytest.fixture
    def invalid_workspace(self, tmp_path):
        """Create an invalid workspace DSL"""
        workspace_file = tmp_path / "invalid.dsl"
        
        # Invalid DSL with undefined element reference
        invalid_content = """
workspace "Invalid" {
    model {
        user = person "User"
        user -> undefinedElement "Invalid relationship"
    }
    
    views {
    }
}
"""
        workspace_file.write_text(invalid_content)
        return workspace_file
    
    def test_validate_valid_workspace(self, cli, sample_workspace):
        """Test validation of valid workspace"""
        result = cli.validate_workspace(sample_workspace)
        
        assert result.valid
        assert result.workspace_file == sample_workspace
        assert len(result.errors) == 0
    
    def test_validate_invalid_workspace(self, cli, invalid_workspace):
        """Test validation of invalid workspace"""
        result = cli.validate_workspace(invalid_workspace)
        
        assert not result.valid
        assert result.workspace_file == invalid_workspace
        assert len(result.errors) > 0
    
    def test_export_to_plantuml(self, cli, sample_workspace, tmp_path):
        """Test PlantUML export"""
        output_dir = tmp_path / "output"
        
        result = cli.export_diagrams(
            workspace_file=sample_workspace,
            format="plantuml",
            output_dir=output_dir
        )
        
        assert result.success
        assert result.format == "plantuml"
        assert len(result.files) > 0
        
        # Verify PlantUML files were created
        puml_files = list(output_dir.glob("*.puml"))
        assert len(puml_files) > 0
    
    def test_export_to_mermaid(self, cli, sample_workspace, tmp_path):
        """Test Mermaid export"""
        output_dir = tmp_path / "output"
        
        result = cli.export_diagrams(
            workspace_file=sample_workspace,
            format="mermaid",
            output_dir=output_dir
        )
        
        assert result.success
        assert result.format == "mermaid"
        assert len(result.files) > 0
    
    def test_export_to_dot(self, cli, sample_workspace, tmp_path):
        """Test DOT export"""
        output_dir = tmp_path / "output"
        
        result = cli.export_diagrams(
            workspace_file=sample_workspace,
            format="dot",
            output_dir=output_dir
        )
        
        assert result.success
        assert result.format == "dot"
        assert len(result.files) > 0
    
    def test_inspect_workspace(self, cli, sample_workspace):
        """Test workspace inspection"""
        result = cli.inspect_workspace(sample_workspace)
        
        assert result["success"]
        assert "workspace_file" in result
        assert "output" in result
    
    def test_version_info(self, cli):
        """Test version information retrieval"""
        info = cli.get_version_info()
        
        assert "structurizr_cli" in info
        assert "java_version" in info
        assert "cli_path" in info
        assert info["structurizr_cli"] == "2025.11.09"
    
    def test_export_nonexistent_workspace_fails(self, cli, tmp_path):
        """Test that exporting non-existent workspace raises error"""
        nonexistent = tmp_path / "nonexistent.dsl"
        
        with pytest.raises(StructurizrError):
            cli.export_diagrams(
                workspace_file=nonexistent,
                format="plantuml",
                output_dir=tmp_path
            )
    
    def test_validate_nonexistent_workspace_fails(self, cli, tmp_path):
        """Test that validating non-existent workspace raises error"""
        nonexistent = tmp_path / "nonexistent.dsl"
        
        with pytest.raises(StructurizrError):
            cli.validate_workspace(nonexistent)
