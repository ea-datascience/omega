"""
Structurizr CLI Integration Module

This module provides Python integration with Structurizr CLI for architecture
diagram generation, validation, and export.

Structurizr is designed for C4 model diagrams and supports export to:
- PlantUML
- Mermaid
- DOT (Graphviz)
- WebSequenceDiagrams
- Ilograph

Features:
- DSL workspace validation
- Diagram export to multiple formats
- Workspace inspection
- Python-friendly API

Dependencies:
- Structurizr CLI 2025.11.09+
- Java 17+

Version Information:
- Structurizr CLI: 2025.11.09
"""

import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass

from src.utils.java_utils import JavaEnvironment, JavaEnvironmentManager

logger = logging.getLogger(__name__)


# Type aliases for export formats
ExportFormat = Literal[
    "plantuml",
    "mermaid",
    "dot",
    "websequencediagrams",
    "ilograph",
    "json"
]


class StructurizrError(Exception):
    """Base exception for Structurizr operations"""
    pass


@dataclass
class ExportResult:
    """Result of diagram export operation"""
    format: str
    output_dir: Path
    files: List[Path]
    success: bool
    message: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "format": self.format,
            "output_dir": str(self.output_dir),
            "files": [str(f) for f in self.files],
            "success": self.success,
            "message": self.message
        }


@dataclass
class ValidationResult:
    """Result of DSL validation"""
    valid: bool
    workspace_file: Path
    message: str
    errors: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "valid": self.valid,
            "workspace_file": str(self.workspace_file),
            "message": self.message,
            "errors": self.errors
        }


class StructurizrCLI:
    """
    Python wrapper for Structurizr CLI.
    
    Provides high-level API for architecture diagram generation and validation
    using the Structurizr DSL and C4 model.
    
    Version Information:
    - Structurizr CLI: 2025.11.09
    """
    
    STRUCTURIZR_VERSION = "2025.11.09"
    CLI_PATH = Path("/opt/structurizr-cli/structurizr.sh")
    
    def __init__(self, cli_path: Optional[Path] = None, java_env: Optional[JavaEnvironment] = None):
        """
        Initialize Structurizr CLI integration.
        
        Args:
            cli_path: Path to structurizr.sh. If None, uses default /opt/structurizr-cli/structurizr.sh
            java_env: JavaEnvironment instance. If None, detects automatically.
            
        Raises:
            StructurizrError: If CLI or Java environment is not properly configured
        """
        self.cli_path = cli_path or self.CLI_PATH
        
        if not self.cli_path.exists():
            raise StructurizrError(
                f"Structurizr CLI not found at {self.cli_path}. "
                f"Please run install-structurizr.sh first."
            )
        
        # Verify Java environment
        if java_env is None:
            java_manager = JavaEnvironmentManager()
            try:
                self.java_env = java_manager.detect_java_environment()
            except Exception as e:
                raise StructurizrError(
                    f"Failed to detect Java environment: {e}"
                )
        else:
            self.java_env = java_env
        
        if not self.java_env.is_valid:
            raise StructurizrError(
                f"Java 17+ is required but found Java {self.java_env.major_version}. "
                "Please install Java 17 or later."
            )
        
        logger.info(f"Structurizr CLI initialized: {self.cli_path}")
        logger.info(f"Java version: {self.java_env.version}")
    
    def export_diagrams(
        self,
        workspace_file: Path,
        format: ExportFormat,
        output_dir: Optional[Path] = None
    ) -> ExportResult:
        """
        Export diagrams from a Structurizr DSL workspace.
        
        Args:
            workspace_file: Path to workspace.dsl file
            format: Export format (plantuml, mermaid, dot, websequencediagrams, ilograph, json)
            output_dir: Output directory. If None, uses temp directory.
            
        Returns:
            ExportResult containing exported files and status
            
        Raises:
            StructurizrError: If export fails or workspace file doesn't exist
            
        Example:
            >>> cli = StructurizrCLI()
            >>> result = cli.export_diagrams(
            ...     workspace_file=Path("workspace.dsl"),
            ...     format="plantuml",
            ...     output_dir=Path("/workspace/diagrams")
            ... )
            >>> print(f"Exported {len(result.files)} files")
        """
        if not workspace_file.exists():
            raise StructurizrError(f"Workspace file not found: {workspace_file}")
        
        if output_dir is None:
            output_dir = Path(tempfile.mkdtemp(prefix="structurizr-export-"))
        else:
            output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Exporting diagrams from {workspace_file} to {format}")
        
        # Build command
        cmd = [
            str(self.cli_path),
            "export",
            "--workspace", str(workspace_file),
            "--format", format,
            "--output", str(output_dir)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Find exported files
            exported_files = list(output_dir.glob("*"))
            
            logger.info(f"Export successful: {len(exported_files)} files generated")
            
            return ExportResult(
                format=format,
                output_dir=output_dir,
                files=exported_files,
                success=True,
                message=f"Successfully exported {len(exported_files)} diagram(s)"
            )
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Export failed: {e.stderr}"
            logger.error(error_msg)
            
            return ExportResult(
                format=format,
                output_dir=output_dir,
                files=[],
                success=False,
                message=error_msg
            )
    
    def validate_workspace(self, workspace_file: Path) -> ValidationResult:
        """
        Validate a Structurizr DSL workspace.
        
        Args:
            workspace_file: Path to workspace.dsl file
            
        Returns:
            ValidationResult with validation status and any errors
            
        Raises:
            StructurizrError: If workspace file doesn't exist
            
        Example:
            >>> cli = StructurizrCLI()
            >>> result = cli.validate_workspace(Path("workspace.dsl"))
            >>> if result.valid:
            ...     print("Workspace is valid!")
        """
        if not workspace_file.exists():
            raise StructurizrError(f"Workspace file not found: {workspace_file}")
        
        logger.info(f"Validating workspace: {workspace_file}")
        
        cmd = [
            str(self.cli_path),
            "validate",
            "--workspace", str(workspace_file)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Workspace validation successful")
            
            return ValidationResult(
                valid=True,
                workspace_file=workspace_file,
                message="Workspace is valid",
                errors=[]
            )
            
        except subprocess.CalledProcessError as e:
            # Errors appear in both stdout and stderr, prefer stdout for detailed messages
            error_output = (e.stdout or e.stderr).strip()
            errors = [line for line in error_output.split('\n') if line.strip()]
            
            logger.warning(f"Workspace validation failed: {len(errors)} error(s)")
            
            return ValidationResult(
                valid=False,
                workspace_file=workspace_file,
                message=f"Validation failed with {len(errors)} error(s)",
                errors=errors
            )
    
    def inspect_workspace(self, workspace_file: Path) -> Dict:
        """
        Inspect a Structurizr workspace and return metadata.
        
        Args:
            workspace_file: Path to workspace.dsl or .json file
            
        Returns:
            Dictionary with workspace metadata
            
        Raises:
            StructurizrError: If workspace file doesn't exist or inspection fails
        """
        if not workspace_file.exists():
            raise StructurizrError(f"Workspace file not found: {workspace_file}")
        
        logger.info(f"Inspecting workspace: {workspace_file}")
        
        cmd = [
            str(self.cli_path),
            "inspect",
            "--workspace", str(workspace_file)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False  # Don't raise on non-zero exit (warnings use exit code 5)
            )
            
            # Parse output (Structurizr inspect outputs to stdout)
            output = result.stdout.strip()
            
            return {
                "workspace_file": str(workspace_file),
                "output": output,
                "exit_code": result.returncode,
                "success": True  # Even warnings are considered successful inspection
            }
            
        except Exception as e:
            raise StructurizrError(f"Workspace inspection failed: {e}")
    
    def list_elements(self, workspace_file: Path) -> List[str]:
        """
        List all elements in a workspace.
        
        Args:
            workspace_file: Path to workspace.dsl or .json file
            
        Returns:
            List of element identifiers
            
        Raises:
            StructurizrError: If listing fails
        """
        if not workspace_file.exists():
            raise StructurizrError(f"Workspace file not found: {workspace_file}")
        
        logger.info(f"Listing elements in workspace: {workspace_file}")
        
        cmd = [
            str(self.cli_path),
            "list",
            "--workspace", str(workspace_file)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse output lines
            elements = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            
            logger.info(f"Found {len(elements)} elements")
            
            return elements
            
        except subprocess.CalledProcessError as e:
            raise StructurizrError(f"Element listing failed: {e.stderr}")
    
    def get_version_info(self) -> Dict[str, str]:
        """
        Get version information for Structurizr CLI.
        
        Returns:
            Dictionary with version details
        """
        return {
            "structurizr_cli": self.STRUCTURIZR_VERSION,
            "cli_path": str(self.cli_path),
            "java_version": self.java_env.version,
            "java_home": self.java_env.java_home
        }


# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        workspace = Path(sys.argv[1])
        
        cli = StructurizrCLI()
        
        # Validate workspace
        print(f"Validating {workspace}...")
        validation = cli.validate_workspace(workspace)
        
        if validation.valid:
            print("✓ Workspace is valid")
            
            # Export to PlantUML
            print("\nExporting to PlantUML...")
            result = cli.export_diagrams(
                workspace_file=workspace,
                format="plantuml",
                output_dir=Path("/workspace/diagrams")
            )
            
            if result.success:
                print(f"✓ Exported {len(result.files)} diagram(s)")
                for f in result.files:
                    print(f"  - {f}")
            else:
                print(f"✗ Export failed: {result.message}")
        else:
            print("✗ Workspace validation failed:")
            for error in validation.errors:
                print(f"  - {error}")
    else:
        print("Usage: python -m src.utils.structurizr_cli <workspace.dsl>")
        
        # Show version info
        try:
            cli = StructurizrCLI()
            info = cli.get_version_info()
            print(f"\nStructurizr CLI {info['structurizr_cli']}")
            print(f"Java: {info['java_version']}")
        except StructurizrError as e:
            print(f"\nError: {e}")
