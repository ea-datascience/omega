"""Java parser management and evaluation utilities.

This module provides reproducible installation and management of Java parsers
for static analysis. Supports tree-sitter-java and JavaParser with version control.

Principles:
- All installations are scripted and reproducible
- Versions are pinned and documented
- No ad-hoc installations or manual downloads
- All configurations stored in version control
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ParserType(Enum):
    """Supported Java parser types."""
    TREE_SITTER = "tree-sitter-java"
    JAVAPARSER = "javaparser"


@dataclass
class ParserInfo:
    """Information about an installed parser."""
    parser_type: ParserType
    version: str
    installed: bool
    location: Optional[Path]
    supports_java_17: bool
    supports_records: bool
    supports_pattern_matching: bool
    supports_sealed_classes: bool


class JavaParserManager:
    """Manages Java parser installation and evaluation."""
    
    # Pinned versions for reproducibility
    TREE_SITTER_VERSION = "0.23.5"
    TREE_SITTER_CORE_VERSION = "0.23.2"
    JAVAPARSER_VERSION = "3.26.4"  # For future Java-based integration
    
    def __init__(self):
        """Initialize parser manager."""
        self.installed_parsers: Dict[ParserType, ParserInfo] = {}
    
    def install_tree_sitter_java(self, force: bool = False) -> bool:
        """Install tree-sitter-java parser with Python bindings.
        
        Args:
            force: Force reinstallation even if already installed
            
        Returns:
            True if installation succeeded
        """
        logger.info(f"Installing tree-sitter-java v{self.TREE_SITTER_VERSION}")
        
        try:
            # Check if already installed
            if not force:
                try:
                    import tree_sitter_java
                    current_version = getattr(tree_sitter_java, '__version__', 'unknown')
                    if current_version == self.TREE_SITTER_VERSION:
                        logger.info(f"tree-sitter-java v{self.TREE_SITTER_VERSION} already installed")
                        return True
                except ImportError:
                    pass
            
            # Detect package manager (uv or pip)
            use_uv = False
            try:
                result = subprocess.run(
                    ["uv", "--version"],
                    capture_output=True,
                    check=False
                )
                if result.returncode == 0:
                    use_uv = True
                    logger.info("Using uv package manager")
            except FileNotFoundError:
                logger.info("Using pip package manager")
            
            if use_uv:
                # Install tree-sitter core using uv
                logger.info(f"Installing tree-sitter core v{self.TREE_SITTER_CORE_VERSION}")
                subprocess.run(
                    ["uv", "pip", "install", 
                     f"tree-sitter=={self.TREE_SITTER_CORE_VERSION}"],
                    check=True,
                    capture_output=True
                )
                
                # Install tree-sitter-java using uv
                logger.info(f"Installing tree-sitter-java v{self.TREE_SITTER_VERSION}")
                subprocess.run(
                    ["uv", "pip", "install", 
                     f"tree-sitter-java=={self.TREE_SITTER_VERSION}"],
                    check=True,
                    capture_output=True
                )
            else:
                # Install tree-sitter core using pip
                logger.info(f"Installing tree-sitter core v{self.TREE_SITTER_CORE_VERSION}")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", 
                     f"tree-sitter=={self.TREE_SITTER_CORE_VERSION}"],
                    check=True,
                    capture_output=True
                )
                
                # Install tree-sitter-java using pip
                logger.info(f"Installing tree-sitter-java v{self.TREE_SITTER_VERSION}")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", 
                     f"tree-sitter-java=={self.TREE_SITTER_VERSION}"],
                    check=True,
                    capture_output=True
                )
            
            # Verify installation
            import tree_sitter_java
            logger.info("tree-sitter-java installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install tree-sitter-java: {e.stderr.decode() if e.stderr else str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error installing tree-sitter-java: {e}")
            return False
    
    def get_parser_info(self, parser_type: ParserType) -> ParserInfo:
        """Get information about a parser.
        
        Args:
            parser_type: Type of parser to check
            
        Returns:
            ParserInfo object with parser details
        """
        if parser_type == ParserType.TREE_SITTER:
            return self._get_tree_sitter_info()
        elif parser_type == ParserType.JAVAPARSER:
            return self._get_javaparser_info()
        else:
            raise ValueError(f"Unknown parser type: {parser_type}")
    
    def _get_tree_sitter_info(self) -> ParserInfo:
        """Get tree-sitter-java parser information."""
        try:
            import tree_sitter_java
            version = getattr(tree_sitter_java, '__version__', 'unknown')
            location = Path(tree_sitter_java.__file__).parent
            
            return ParserInfo(
                parser_type=ParserType.TREE_SITTER,
                version=version,
                installed=True,
                location=location,
                supports_java_17=True,
                supports_records=True,
                supports_pattern_matching=True,
                supports_sealed_classes=True
            )
        except ImportError:
            return ParserInfo(
                parser_type=ParserType.TREE_SITTER,
                version="not installed",
                installed=False,
                location=None,
                supports_java_17=False,
                supports_records=False,
                supports_pattern_matching=False,
                supports_sealed_classes=False
            )
    
    def _get_javaparser_info(self) -> ParserInfo:
        """Get JavaParser information (Java library - requires Java runtime)."""
        # JavaParser is a Java library, would require Java interop
        # For now, document as future enhancement
        return ParserInfo(
            parser_type=ParserType.JAVAPARSER,
            version="future",
            installed=False,
            location=None,
            supports_java_17=True,
            supports_records=True,
            supports_pattern_matching=True,
            supports_sealed_classes=True
        )
    
    def evaluate_parsers(self) -> List[Tuple[ParserType, ParserInfo]]:
        """Evaluate all available parsers.
        
        Returns:
            List of (parser_type, parser_info) tuples
        """
        results = []
        for parser_type in ParserType:
            info = self.get_parser_info(parser_type)
            results.append((parser_type, info))
            self.installed_parsers[parser_type] = info
        
        return results
    
    def print_evaluation_report(self):
        """Print parser evaluation report."""
        print("\n" + "="*80)
        print("Java Parser Evaluation Report")
        print("="*80 + "\n")
        
        results = self.evaluate_parsers()
        
        for parser_type, info in results:
            print(f"Parser: {parser_type.value}")
            print(f"  Version: {info.version}")
            print(f"  Installed: {'✓' if info.installed else '✗'}")
            if info.location:
                print(f"  Location: {info.location}")
            print(f"  Java 17+ Support: {'✓' if info.supports_java_17 else '✗'}")
            print(f"  Records Support: {'✓' if info.supports_records else '✗'}")
            print(f"  Pattern Matching: {'✓' if info.supports_pattern_matching else '✗'}")
            print(f"  Sealed Classes: {'✓' if info.supports_sealed_classes else '✗'}")
            print()
        
        print("="*80)
        print("Recommendation:")
        print("="*80)
        print("\nBased on evaluation:")
        print("  - tree-sitter-java: Native Python library, excellent Java 17+ support")
        print("  - Recommended for production use in omega-analysis")
        print("  - Supports all modern Java syntax (records, pattern matching, sealed classes)")
        print("\nInstallation command:")
        print(f"  uv pip install tree-sitter=={self.TREE_SITTER_CORE_VERSION} tree-sitter-java=={self.TREE_SITTER_VERSION}")
        print("\nVersions are pinned for reproducibility across all developers.")
        print("="*80 + "\n")
    
    def get_recommended_parser(self) -> ParserType:
        """Get recommended parser for Java 17+ analysis.
        
        Returns:
            Recommended ParserType
        """
        return ParserType.TREE_SITTER


def install_recommended_parser(force: bool = False) -> bool:
    """Install the recommended Java parser.
    
    Args:
        force: Force reinstallation
        
    Returns:
        True if installation succeeded
    """
    manager = JavaParserManager()
    return manager.install_tree_sitter_java(force=force)


def main():
    """CLI entry point for parser management."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Java Parser Manager - Reproducible parser installation and evaluation"
    )
    parser.add_argument(
        "command",
        choices=["evaluate", "install", "info"],
        help="Command to execute"
    )
    parser.add_argument(
        "--parser",
        choices=["tree-sitter", "javaparser"],
        help="Specific parser to operate on"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reinstallation"
    )
    
    args = parser.parse_args()
    
    manager = JavaParserManager()
    
    if args.command == "evaluate":
        manager.print_evaluation_report()
    
    elif args.command == "install":
        parser_type = ParserType.TREE_SITTER if args.parser == "tree-sitter" else None
        if parser_type is None or parser_type == ParserType.TREE_SITTER:
            success = manager.install_tree_sitter_java(force=args.force)
            if success:
                print("Installation successful!")
            else:
                print("Installation failed!")
                sys.exit(1)
        else:
            print(f"Installation not yet supported for {args.parser}")
            sys.exit(1)
    
    elif args.command == "info":
        if args.parser:
            parser_type = ParserType.TREE_SITTER if args.parser == "tree-sitter" else ParserType.JAVAPARSER
            info = manager.get_parser_info(parser_type)
            print(f"\n{parser_type.value}:")
            print(f"  Version: {info.version}")
            print(f"  Installed: {'✓' if info.installed else '✗'}")
            if info.location:
                print(f"  Location: {info.location}")
        else:
            manager.print_evaluation_report()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
