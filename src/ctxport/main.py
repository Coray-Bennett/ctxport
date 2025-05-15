"""
Entry point for Code Context Exporter
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from ctxport.config import ConfigManager
from ctxport.core import CodeExporter, ClipboardManager
from ctxport.utils.path_utils import normalize_path


# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger("ctxport")


def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser.
    
    Returns:
        The configured argument parser
    """
    parser = argparse.ArgumentParser(
        description='Export codebase context to markdown for AI prompts'
    )
    
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to export (default: current directory)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: copy to clipboard)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    # Configuration options
    config_group = parser.add_argument_group('configuration options')
    
    config_group.add_argument(
        '--init-config',
        action='store_true',
        help='Create an example configuration file in the current directory'
    )
    
    config_group.add_argument(
        '--init-global-config',
        action='store_true',
        help='Create an example global configuration file'
    )
    
    return parser


def handle_config_initialization(args: argparse.Namespace, config_manager: ConfigManager) -> bool:
    """
    Handle configuration initialization commands.
    
    Args:
        args: The parsed command line arguments
        config_manager: The configuration manager
        
    Returns:
        True if a configuration was initialized, False otherwise
    """
    if args.init_config:
        config_path = Path('.ctxport.json')
        success = config_manager.create_example_config(config_path)
        if success:
            print(f"Created example configuration at: {config_path.resolve()}")
        else:
            print(f"Failed to create example configuration")
        return True
    
    if args.init_global_config:
        config_dir = Path.home() / '.config' / 'ctxport'
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / 'ctxport.json'
        success = config_manager.create_example_config(config_path)
        if success:
            print(f"Created global example configuration at: {config_path}")
        else:
            print(f"Failed to create global example configuration")
        return True
    
    return False


def write_to_file(file_path: Path, content: str) -> bool:
    """
    Write content to a file.
    
    Args:
        file_path: The path to write to
        content: The content to write
        
    Returns:
        True on success, False on failure
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error writing to file: {e}")
        return False


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for the Code Context Exporter.
    
    Args:
        argv: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    # Configure logging level
    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.verbose:
        logger.setLevel(logging.INFO)
    
    # Initialize the configuration manager
    config_manager = ConfigManager()
    
    # Handle configuration initialization commands
    if handle_config_initialization(args, config_manager):
        return 0
    
    # Get the directory to export
    try:
        root_dir = normalize_path(args.directory)
        if not root_dir.exists():
            logger.error(f"Directory does not exist: {root_dir}")
            return 1
        if not root_dir.is_dir():
            logger.error(f"Not a directory: {root_dir}")
            return 1
    except Exception as e:
        logger.error(f"Invalid directory: {e}")
        return 1
    
    # Initialize exporter
    exporter = CodeExporter(config_manager)
    exporter.set_directory(root_dir)
    
    # Export the directory
    try:
        output_content, file_count = exporter.export_directory(args.verbose)
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return 1
    
    # Output the results
    if args.output:
        output_path = Path(args.output)
        if write_to_file(output_path, output_content):
            print(f"Successfully exported {file_count} files to: {output_path.resolve()}")
        else:
            return 1
    else:
        # Try to copy to clipboard
        clipboard = ClipboardManager()
        if clipboard.copy_to_clipboard(output_content):
            print(f"Successfully copied {file_count} files to clipboard")
        else:
            print("Error: Could not copy to clipboard. Printing to stdout instead:")
            print("-" * 40)
            print(output_content)
            return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())