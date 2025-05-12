"""
Configuration system for Code Context Exporter
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
import fnmatch
import os


@dataclass
class Config:
    """Configuration for Code Context Exporter"""
    # Language mappings for syntax highlighting
    language_map: Dict[str, str] = field(default_factory=dict)
    
    # Extensions considered as text files
    text_extensions: Set[str] = field(default_factory=set)
    
    # Ignore patterns
    ignore_patterns: List[str] = field(default_factory=list)
    
    def merge(self, other: 'Config') -> 'Config':
        """Merge another config into this one, with other's values taking precedence"""
        merged = Config()
        
        # Merge language map
        merged.language_map = {**self.language_map, **other.language_map}
        
        # Merge text extensions
        merged.text_extensions = self.text_extensions | other.text_extensions
        
        # Merge ignore patterns
        merged.ignore_patterns = self.ignore_patterns + other.ignore_patterns
        
        return merged


class ConfigManager:
    """Manage configuration loading and merging"""
    
    DEFAULT_CONFIG_NAME = '.ctxport.json'
    GLOBAL_CONFIG_NAME = 'ctxport.json'
    
    def __init__(self):
        self._default_config = self._get_default_config()
        self._global_config: Optional[Config] = None
        self._cached_configs: Dict[Path, Config] = {}
    
    def _get_default_config(self) -> Config:
        """Get the default configuration"""
        return Config(
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
                '.dockerfile': 'dockerfile',
                '.xml': 'xml',
                '.vue': 'vue',
                '.svelte': 'svelte',
            },
            text_extensions={
                '.txt', '.md', '.yml', '.yaml', '.json', '.xml', '.html', '.css',
                '.js', '.jsx', '.ts', '.tsx', '.py', '.rb', '.php', '.java', '.cpp',
                '.c', '.h', '.rs', '.go', '.sh', '.bash', '.zsh', '.fish', '.ps1',
                '.dockerfile', '.gitignore', '.env', '.conf', '.cfg', '.ini',
                '.toml', '.lock', '.sum', '.mod'
            }
        )
    
    def _load_global_config(self) -> Config:
        """Load global configuration from user's home directory"""
        if self._global_config is not None:
            return self._global_config
        
        config_locations = [
            Path.home() / '.config' / 'ctxport' / self.GLOBAL_CONFIG_NAME,
            Path.home() / f'.{self.GLOBAL_CONFIG_NAME}'
        ]
        
        # Try XDG_CONFIG_HOME first if available
        xdg_config = os.environ.get('XDG_CONFIG_HOME')
        if xdg_config:
            config_locations.insert(0, Path(xdg_config) / 'ctxport' / self.GLOBAL_CONFIG_NAME)
        
        for config_path in config_locations:
            if config_path.exists():
                try:
                    self._global_config = self._load_config_file(config_path)
                    return self._global_config
                except Exception:
                    # If we can't load the global config, fall back to default
                    pass
        
        # No global config found, use empty Config
        self._global_config = Config()
        return self._global_config
    
    def _load_config_file(self, path: Path) -> Config:
        """Load configuration from a file"""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            config = Config()
            
            # Load language map
            if 'language_map' in data and isinstance(data['language_map'], dict):
                config.language_map = data['language_map']
            
            # Load text extensions
            if 'text_extensions' in data and isinstance(data['text_extensions'], list):
                config.text_extensions = set(data['text_extensions'])
            
            # Load ignore patterns
            if 'ignore_patterns' in data and isinstance(data['ignore_patterns'], list):
                config.ignore_patterns = data['ignore_patterns']
            
            return config
            
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Failed to load config from {path}: {e}", file=sys.stderr)
            return Config()
    
    def get_config_for_directory(self, directory: Path) -> Config:
        """Get the merged configuration for a specific directory"""
        directory = directory.resolve()
        
        if directory in self._cached_configs:
            return self._cached_configs[directory]
        
        # Start with default config
        merged_config = self._default_config
        
        # Merge with global config
        global_config = self._load_global_config()
        merged_config = merged_config.merge(global_config)
        
        # Look for directory-specific configs, starting from root and going down
        config_files = []
        current = directory
        while current != current.parent:
            config_file = current / self.DEFAULT_CONFIG_NAME
            if config_file.exists():
                config_files.append(config_file)
            current = current.parent
        
        # Apply configs from root to specific directory
        for config_file in reversed(config_files):
            dir_config = self._load_config_file(config_file)
            merged_config = merged_config.merge(dir_config)
        
        self._cached_configs[directory] = merged_config
        return merged_config
    
    def create_example_config(self, path: Path):
        """Create an example configuration file"""
        example_config = {
            "language_map": {
                ".custom": "custom-language",
                ".myext": "mylang",
                "# Add more mappings here": "..."
            },
            "text_extensions": [
                ".custom",
                ".myext",
                "# Add more extensions here"
            ],
            "ignore_patterns": [
                "*.log",
                "temp/",
                "# Add more patterns here"
            ]
        }
        
        try:
            with open(path, 'w') as f:
                json.dump(example_config, f, indent=2)
            print(f"Created example configuration at: {path}")
        except Exception as e:
            print(f"Error creating example config: {e}", file=sys.stderr)