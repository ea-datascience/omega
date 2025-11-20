"""
Microsoft Application Inspector CLI Python Wrapper

This module provides a Python interface to Microsoft Application Inspector CLI for
analyzing source code patterns, identifying technologies, security issues, and
migration readiness indicators.

Features:
- Analyze source code for patterns and technologies
- Export results in HTML, JSON, or text formats
- Tag-based analysis and comparison
- Integration with Omega migration assessment workflow

Usage:
    from src.utils.appinspector_cli import AppInspectorCLI
    
    appinspector = AppInspectorCLI()
    
    # Analyze a codebase
    result = appinspector.analyze(
        source_path="/path/to/source",
        output_file="analysis.html",
        output_format="html"
    )
    
    # Get tags only (fast)
    tags = appinspector.analyze_tags_only(
        source_path="/path/to/source"
    )

References:
- GitHub: https://github.com/microsoft/ApplicationInspector
- Documentation: https://github.com/microsoft/ApplicationInspector/wiki
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union


class AppInspectorCLI:
    """Python wrapper for Microsoft Application Inspector CLI.
    
    This class provides a Pythonic interface to the AppInspector command-line tool,
    enabling automated code analysis for technology detection, security patterns,
    and migration assessment.
    
    Attributes:
        cli_path (str): Path to the appinspector executable
        default_timeout (int): Default timeout for analysis operations in seconds
    """
    
    def __init__(
        self,
        cli_path: str = "appinspector",
        default_timeout: int = 600
    ):
        """Initialize AppInspector CLI wrapper.
        
        Args:
            cli_path: Path to appinspector executable (default: "appinspector")
            default_timeout: Default timeout for operations in seconds (default: 600)
        
        Raises:
            FileNotFoundError: If appinspector CLI is not found
        """
        self.cli_path = cli_path
        self.default_timeout = default_timeout
        self._verify_installation()
    
    def _verify_installation(self) -> None:
        """Verify AppInspector CLI is installed and accessible.
        
        Raises:
            FileNotFoundError: If appinspector is not found or not executable
        """
        try:
            result = subprocess.run(
                [self.cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if "ApplicationInspector" not in result.stdout and "ApplicationInspector" not in result.stderr:
                raise FileNotFoundError(
                    f"AppInspector CLI not found at {self.cli_path}"
                )
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            raise FileNotFoundError(
                f"AppInspector CLI not accessible: {e}\n"
                f"Install using: /workspace/tools/src/utils/install-appinspector.sh"
            )
    
    def analyze(
        self,
        source_path: Union[str, Path],
        output_file: Optional[Union[str, Path]] = None,
        output_format: str = "html",
        tags_only: bool = False,
        no_file_metadata: bool = False,
        context_lines: int = 3,
        ignore_default_rules: bool = False,
        custom_rules_path: Optional[Union[str, Path]] = None,
        timeout: Optional[int] = None
    ) -> Dict:
        """Analyze source code using Application Inspector.
        
        Args:
            source_path: Path to source code directory or file
            output_file: Path to output file (optional, returns to stdout if None)
            output_format: Output format - "html", "json", or "text" (default: "html")
            tags_only: Only extract tags without detailed match data (default: False)
            no_file_metadata: Skip file metadata collection (default: False)
            context_lines: Number of context lines around matches (default: 3)
            ignore_default_rules: Exclude default bundled rules (default: False)
            custom_rules_path: Path to custom rules directory or file (optional)
            timeout: Timeout in seconds (default: use instance default_timeout)
        
        Returns:
            Dictionary with analysis results including:
            - success: Whether analysis succeeded
            - output_file: Path to output file (if created)
            - stdout: Command output
            - stderr: Command errors
            - tags: Detected tags (if available)
        
        Raises:
            FileNotFoundError: If source_path doesn't exist
            ValueError: If invalid output_format specified
            subprocess.TimeoutExpired: If analysis exceeds timeout
        """
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Source path not found: {source_path}")
        
        valid_formats = ["html", "json", "text"]
        if output_format not in valid_formats:
            raise ValueError(
                f"Invalid output format: {output_format}. "
                f"Must be one of {valid_formats}"
            )
        
        # Build command
        cmd = [
            self.cli_path,
            "analyze",
            "-s", str(source),
            "-f", output_format,
            "-C", str(context_lines)
        ]
        
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cmd.extend(["-o", str(output_path)])
        
        if tags_only:
            cmd.append("-t")
        
        if no_file_metadata:
            cmd.append("-n")
        
        if ignore_default_rules:
            cmd.append("-i")
        
        if custom_rules_path:
            rules_path = Path(custom_rules_path)
            if not rules_path.exists():
                raise FileNotFoundError(f"Custom rules path not found: {custom_rules_path}")
            cmd.extend(["-r", str(rules_path)])
        
        # Execute analysis
        timeout_value = timeout if timeout is not None else self.default_timeout
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_value
            )
            
            # Parse output if JSON format
            tags = None
            if output_format == "json" and output_file:
                try:
                    with open(output_file, 'r') as f:
                        data = json.load(f)
                        tags = data.get('tags', [])
                except (json.JSONDecodeError, FileNotFoundError):
                    pass
            
            return {
                "success": result.returncode == 0,
                "output_file": str(output_file) if output_file else None,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "tags": tags,
                "return_code": result.returncode
            }
        
        except subprocess.TimeoutExpired:
            raise subprocess.TimeoutExpired(
                cmd=" ".join(cmd),
                timeout=timeout_value
            )
    
    def analyze_tags_only(
        self,
        source_path: Union[str, Path],
        output_file: Optional[Union[str, Path]] = None,
        timeout: Optional[int] = None
    ) -> List[str]:
        """Fast analysis to extract only tags without detailed match data.
        
        Args:
            source_path: Path to source code directory or file
            output_file: Optional path to save JSON output
            timeout: Timeout in seconds (default: use instance default_timeout)
        
        Returns:
            List of detected tags
        
        Raises:
            FileNotFoundError: If source_path doesn't exist
        """
        result = self.analyze(
            source_path=source_path,
            output_file=output_file,
            output_format="json",
            tags_only=True,
            timeout=timeout
        )
        
        if result["tags"]:
            return result["tags"]
        
        # Try to parse from output file if available
        if output_file and Path(output_file).exists():
            with open(output_file, 'r') as f:
                data = json.load(f)
                return data.get('tags', [])
        
        return []
    
    def export_tags(
        self,
        output_file: Union[str, Path],
        custom_rules_path: Optional[Union[str, Path]] = None,
        ignore_default_rules: bool = False
    ) -> Dict:
        """Export list of available tags from rules without scanning code.
        
        Args:
            output_file: Path to output file
            custom_rules_path: Path to custom rules directory or file (optional)
            ignore_default_rules: Exclude default bundled rules (default: False)
        
        Returns:
            Dictionary with export results
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            self.cli_path,
            "exporttags",
            "-o", str(output_path)
        ]
        
        if ignore_default_rules:
            cmd.append("-i")
        
        if custom_rules_path:
            rules_path = Path(custom_rules_path)
            if not rules_path.exists():
                raise FileNotFoundError(f"Custom rules path not found: {custom_rules_path}")
            cmd.extend(["-r", str(rules_path)])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "output_file": str(output_path),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    
    def verify_rules(
        self,
        rules_path: Union[str, Path]
    ) -> Dict:
        """Verify custom rules syntax is valid.
        
        Args:
            rules_path: Path to custom rules directory or file
        
        Returns:
            Dictionary with verification results including:
            - valid: Whether rules are valid
            - stdout: Command output
            - stderr: Validation errors
        """
        rules = Path(rules_path)
        if not rules.exists():
            raise FileNotFoundError(f"Rules path not found: {rules_path}")
        
        cmd = [
            self.cli_path,
            "verifyrules",
            "-r", str(rules)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "valid": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    
    def get_version(self) -> str:
        """Get AppInspector CLI version.
        
        Returns:
            Version string
        """
        result = subprocess.run(
            [self.cli_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Parse version from output
        output = result.stdout + result.stderr
        for line in output.split('\n'):
            if "ApplicationInspector" in line and any(c.isdigit() for c in line):
                return line.strip()
        
        return "Unknown"


def main():
    """CLI interface for testing AppInspector wrapper."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.utils.appinspector_cli <source_path> [output_file]")
        print("\nExample:")
        print("  python -m src.utils.appinspector_cli /path/to/source analysis.html")
        sys.exit(1)
    
    source_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "appinspector_analysis.html"
    
    try:
        appinspector = AppInspectorCLI()
        print(f"AppInspector Version: {appinspector.get_version()}")
        print(f"\nAnalyzing: {source_path}")
        print(f"Output: {output_file}")
        print("\nRunning analysis...")
        
        result = appinspector.analyze(
            source_path=source_path,
            output_file=output_file,
            output_format="html"
        )
        
        if result["success"]:
            print(f"\n✓ Analysis complete!")
            print(f"  Report: {result['output_file']}")
            if result["tags"]:
                print(f"  Tags found: {len(result['tags'])}")
        else:
            print(f"\n✗ Analysis failed")
            print(f"  Error: {result['stderr']}")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
