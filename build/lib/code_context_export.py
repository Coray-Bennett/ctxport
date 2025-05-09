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

# Common file extensions to programming languages mapping
LANGUAGE_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.jsx': 'jsx',
    '.ts': 'typescript',
    '.tsx': 'tsx',
    '.html': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.sass': 'sass',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.md': 'markdown',
    '.sh': 'bash',
    '.bash': 'bash',
    '.zsh': 'zsh',
    '.fish': 'fish',
    '.ps1': 'powershell',
    '.c': 'c',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp',
    '.hxx': 'cpp',
    '.rs': 'rust',
    '.go': 'go',
    '.java': 'java',
    '.kt': 'kotlin',
    '.swift': 'swift',
    '.rb': 'ruby',
    '.php': 'php',
    '.sql': 'sql',
    '.r': 'r',
    '.R': 'r',
    '.m': 'matlab',
    '.jl': 'julia',
    '.tex': 'latex',
    '.dockerfile': 'dockerfile',
    '.xml': 'xml',
    '.vue': 'vue',
    '.svelte': 'svelte',
}

def get_language(file_path: Path) -> str:
    """Determine the language for syntax highlighting based on file extension."""
    ext = file_path.suffix.lower()
    
    # Special cases
    if file_path.name.lower() == 'dockerfile':
        return 'dockerfile'
    
    return LANGUAGE_MAP.get(ext, '')

def should_ignore(file_path: Path, ignore_patterns: List[str], root_dir: Path) -> bool:
    """Check if a file should be ignored based on ignore patterns."""
    relative_path = file_path.relative_to(root_dir)
    
    # Always ignore context.ignore file
    if file_path.name == 'context.ignore':
        return True
    
    for pattern in ignore_patterns:
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

def load_ignore_patterns(root_dir: Path) -> List[str]:
    """Load ignore patterns from context.ignore file."""
    ignore_file = root_dir / 'context.ignore'
    patterns = []
    
    if ignore_file.exists():
        with open(ignore_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    
    return patterns

def is_text_file(file_path: Path) -> bool:
    """Check if a file is a text file."""
    try:
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and mime_type.startswith('text/'):
            return True
        
        # Additional checks for common text files
        text_extensions = {
            '.txt', '.md', '.yml', '.yaml', '.json', '.xml', '.html', '.css',
            '.js', '.jsx', '.ts', '.tsx', '.py', '.rb', '.php', '.java', '.cpp',
            '.c', '.h', '.rs', '.go', '.sh', '.bash', '.zsh', '.fish', '.ps1',
            '.dockerfile', '.gitignore', '.env', '.conf', '.cfg', '.ini',
            '.toml', '.lock', '.sum', '.mod'
        }
        
        if file_path.suffix.lower() in text_extensions:
            return True
        
        # Try to read the file as text
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(512)  # Read first 512 bytes
        return True
    except (UnicodeDecodeError, PermissionError, OSError):
        return False

def export_file_content(file_path: Path, root_dir: Path) -> str:
    """Export a single file's content in markdown format."""
    relative_path = file_path.relative_to(root_dir)
    language = get_language(file_path)
    
    content = f"## {relative_path}\n\n"
    content += f"```{language}\n"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content += f.read()
    except Exception as e:
        content += f"# Error reading file: {str(e)}"
    
    content += "\n```\n\n"
    return content

def copy_to_clipboard(text: str) -> bool:
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
    
    args = parser.parse_args()
    
    # Convert to absolute path
    root_dir = Path(args.directory).resolve()
    
    if not root_dir.exists() or not root_dir.is_dir():
        print(f"Error: '{root_dir}' is not a valid directory")
        sys.exit(1)
    
    # Load ignore patterns
    ignore_patterns = load_ignore_patterns(root_dir)
    
    # Collect all files
    output_lines = [f"# Code Context Export: {root_dir.name}\n\n"]
    file_count = 0
    
    for file_path in sorted(root_dir.rglob('*')):
        if file_path.is_file() and not should_ignore(file_path, ignore_patterns, root_dir):
            if is_text_file(file_path):
                if args.verbose:
                    print(f"Processing: {file_path.relative_to(root_dir)}")
                
                output_lines.append(export_file_content(file_path, root_dir))
                file_count += 1
    
    # Join all content
    output_content = ''.join(output_lines)
    
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
        if copy_to_clipboard(output_content):
            print(f"Successfully copied {file_count} files to clipboard")
        else:
            print("Error: Could not copy to clipboard. Printing to stdout instead:")
            print("-" * 40)
            print(output_content)
            sys.exit(1)

if __name__ == '__main__':
    main()