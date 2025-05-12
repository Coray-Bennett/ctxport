#!/usr/bin/env python3
"""
Code Context Exporter - Export codebase context to markdown for AI prompts
"""

import argparse
import sys
import os
import fnmatch
import subprocess
import platform
from pathlib import Path
from typing import List, Set
import mimetypes
from config import ConfigManager, Config


class CodeExporter:
    """Main class for code context export functionality"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config: Config = Config()
    
    def set_directory(self, directory: Path):
        """Set the working directory and load appropriate config"""
        self.directory = directory.resolve()
        self.config = self.config_manager.get_config_for_directory(self.directory)
    
    def get_language(self, file_path: Path) -> str:
        """Determine the language for syntax highlighting based on file extension."""
        ext = file_path.suffix.lower()
        
        # Special cases
        if file_path.name.lower() == 'dockerfile':
            return 'dockerfile'
        
        return self.config.language_map.get(ext, '')
    
    def should_ignore(self, file_path: Path) -> bool:
        """Check if a file should be ignored based on ignore patterns."""
        relative_path = file_path.relative_to(self.directory)
        
        # Always ignore context.ignore file for backward compatibility
        if file_path.name == 'context.ignore':
            return True
        
        # Always ignore config files
        if file_path.name in ['.ctxport.json', 'ctxport.json']:
            return True
        
        for pattern in self.config.ignore_patterns:
            # Handle directory patterns
            if pattern.endswith('/'):
                if any(part == pattern[:-1] for part in relative_path.parts[:-1]):
                    return True
            
            # Check if the pattern matches the relative path
            if fnmatch.fnmatch(str(relative_path), pattern):
                return True
                
            # Check if the pattern matches any part of the path
            for part in relative_path.parts:
                if fnmatch.fnmatch(part, pattern):
                    return True
        
        return False
    
    def load_legacy_ignore_patterns(self) -> List[str]:
        """Load ignore patterns from context.ignore file (backward compatibility)."""
        ignore_file = self.directory / 'context.ignore'
        patterns = []
        
        if ignore_file.exists():
            with open(ignore_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        
        return patterns
    
    def is_text_file(self, file_path: Path) -> bool:
        """Check if a file is a text file."""
        try:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type and mime_type.startswith('text/'):
                return True
            
            # Check against configured text extensions
            if file_path.suffix.lower() in self.config.text_extensions:
                return True
            
            # Try to read the file as text
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(512)  # Read first 512 bytes
            return True
        except (UnicodeDecodeError, PermissionError, OSError):
            return False
    
    def export_file_content(self, file_path: Path) -> str:
        """Export a single file's content in markdown format."""
        relative_path = file_path.relative_to(self.directory)
        language = self.get_language(file_path)
        
        content = f"## {relative_path}\n\n"
        content += f"```{language}\n"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content += f.read()
        except Exception as e:
            content += f"# Error reading file: {str(e)}"
        
        content += "\n```\n\n"
        return content
    
    def copy_to_clipboard(self, text: str) -> bool:
        """Copy text to system clipboard."""
        system = platform.system().lower()
        
        try:
            if system == 'darwin':  # macOS
                process = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, 
                                         stdin=subprocess.PIPE)
                process.communicate(text.encode('utf-8'))
            elif system == 'linux':
                # Try xclip first, then xsel
                try:
                    process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                             stdin=subprocess.PIPE)
                    process.communicate(text.encode('utf-8'))
                except FileNotFoundError:
                    process = subprocess.Popen(['xsel', '--clipboard', '--input'], 
                                             stdin=subprocess.PIPE)
                    process.communicate(text.encode('utf-8'))
            elif system == 'windows':
                process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, 
                                         shell=True)
                process.communicate(text.encode('utf-8'))
            else:
                return False
            
            return process.returncode == 0
        except Exception:
            return False
    
    def export_directory(self, verbose: bool = False) -> tuple[str, int]:
        """Export all files in the directory to markdown format."""
        # Merge legacy ignore patterns with configured ones
        legacy_patterns = self.load_legacy_ignore_patterns()
        self.config.ignore_patterns.extend(legacy_patterns)
        
        # Collect all files
        output_lines = [f"# Code Context Export: {self.directory.name}\n\n"]
        file_count = 0
        
        for file_path in sorted(self.directory.rglob('*')):
            if file_path.is_file() and not self.should_ignore(file_path):
                if self.is_text_file(file_path):
                    if verbose:
                        print(f"Processing: {file_path.relative_to(self.directory)}")
                    
                    output_lines.append(self.export_file_content(file_path))
                    file_count += 1
        
        output_content = ''.join(output_lines)
        return output_content, file_count


def main():
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
        '--init-config',
        action='store_true',
        help='Create an example configuration file in the current directory'
    )
    
    parser.add_argument(
        '--init-global-config',
        action='store_true',
        help='Create an example global configuration file'
    )
    
    args = parser.parse_args()
    
    # Initialize configuration manager
    config_manager = ConfigManager()
    
    # Handle config initialization
    if args.init_config:
        config_path = Path('.ctxport.json')
        config_manager.create_example_config(config_path)
        return
    
    if args.init_global_config:
        config_dir = Path.home() / '.config' / 'ctxport'
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / 'ctxport.json'
        config_manager.create_example_config(config_path)
        return
    
    # Convert to absolute path
    root_dir = Path(args.directory).resolve()
    
    if not root_dir.exists() or not root_dir.is_dir():
        print(f"Error: '{root_dir}' is not a valid directory")
        sys.exit(1)
    
    # Initialize exporter
    exporter = CodeExporter(config_manager)
    exporter.set_directory(root_dir)
    
    # Export the directory
    output_content, file_count = exporter.export_directory(args.verbose)
    
    # Output results
    if args.output:
        output_path = Path(args.output)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
            print(f"Successfully exported {file_count} files to: {output_path}")
        except Exception as e:
            print(f"Error writing to file: {e}")
            sys.exit(1)
    else:
        if exporter.copy_to_clipboard(output_content):
            print(f"Successfully copied {file_count} files to clipboard")
        else:
            print("Error: Could not copy to clipboard. Printing to stdout instead:")
            print("-" * 40)
            print(output_content)
            sys.exit(1)


if __name__ == '__main__':
    main()