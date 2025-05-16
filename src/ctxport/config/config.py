"""
Configuration dataclass
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, ClassVar, Optional


@dataclass
class Config:
    """Configuration for Code Context Exporter"""
    # Language mappings for syntax highlighting by extension
    language_map: Dict[str, str] = field(default_factory=dict)
    
    # Language mappings for specific filenames
    filename_map: Dict[str, str] = field(default_factory=dict)
    
    # Extensions considered as text files
    text_extensions: Set[str] = field(default_factory=set)
    
    # Ignore patterns
    ignore_patterns: List[str] = field(default_factory=list)
    
    # Default language to use when no mapping is found
    default_language: str = ""
    
    # Default configuration as class variable to avoid recreation
    DEFAULT_CONFIG: ClassVar[Optional['Config']] = None
    
    @classmethod
    def get_default_config(cls) -> 'Config':
        """Get the default configuration"""
        if cls.DEFAULT_CONFIG is None:
            cls.DEFAULT_CONFIG = Config(
                language_map={
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
                    '.xml': 'xml',
                    '.vue': 'vue',
                    '.svelte': 'svelte',
                },
                filename_map={
                    'dockerfile': 'dockerfile',
                    'makefile': 'makefile',
                    'gnumakefile': 'makefile',
                    'rakefile': 'ruby',
                    'gemfile': 'ruby',
                    'vagrantfile': 'ruby',
                    'jenkinsfile': 'groovy',
                    'fastfile': 'ruby',
                    'procfile': 'yaml',
                    'podfile': 'ruby',
                    'cakefile': 'coffeescript',
                    'gulpfile': 'javascript',
                    'gruntfile': 'javascript',
                },
                text_extensions={
                    '.txt', '.md', '.yml', '.yaml', '.json', '.xml', '.html', '.css',
                    '.js', '.jsx', '.ts', '.tsx', '.py', '.rb', '.php', '.java', '.cpp',
                    '.c', '.h', '.rs', '.go', '.sh', '.bash', '.zsh', '.fish', '.ps1',
                    '.dockerfile', '.gitignore', '.env', '.conf', '.cfg', '.ini',
                    '.toml', '.lock', '.sum', '.mod'
                },
                ignore_patterns=[
                    '.git/',
                    '__pycache__/',
                    '*.pyc',
                    '*.pyo',
                    '*.pyd',
                    '.DS_Store',
                    '.vscode/',
                    '.idea/',
                    'node_modules/',
                    'venv/',
                    '.env/',
                    '*.min.js',
                    '*.min.css'
                ]
            )
        return cls.DEFAULT_CONFIG
    
    def merge(self, other: 'Config') -> 'Config':
        """Merge another config into this one, with other's values taking precedence"""
        merged = Config()
        
        merged.language_map = {**self.language_map, **other.language_map}
        
        merged.filename_map = {**self.filename_map, **other.filename_map}
        
        merged.text_extensions = self.text_extensions | other.text_extensions
        
        # Merge ignore patterns (preserve order and remove duplicates)
        merged.ignore_patterns = list(dict.fromkeys(self.ignore_patterns + other.ignore_patterns))
        
        merged.default_language = other.default_language or self.default_language
        
        return merged