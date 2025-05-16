"""
Configuration management
"""

import json
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Optional, List
from ctxport.config.config import Config

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manage configuration loading and merging"""
    
    DEFAULT_CONFIG_NAME = '.ctxport.json'
    GLOBAL_CONFIG_NAME = 'ctxport.json'
    LEGACY_IGNORE_FILE = 'context.ignore'
    
    def __init__(self):
        """Initialize the configuration manager"""
        self._global_config: Optional[Config] = None
        self._cached_configs: Dict[Path, Config] = {}
    
    def _load_global_config(self) -> Config:
        """Load global configuration from user's home directory"""
        if self._global_config is not None:
            return self._global_config
        
        config_locations = [
            Path.home() / '.config' / 'ctxport' / self.GLOBAL_CONFIG_NAME,
            Path.home() / f'.{self.GLOBAL_CONFIG_NAME}'
        ]
        
        xdg_config = os.environ.get('XDG_CONFIG_HOME')
        if xdg_config:
            config_locations.insert(0, Path(xdg_config) / 'ctxport' / self.GLOBAL_CONFIG_NAME)
        
        for config_path in config_locations:
            if config_path.exists():
                try:
                    self._global_config = self._load_config_file(config_path)
                    logger.debug(f"Loaded global config from {config_path}")
                    return self._global_config
                except Exception as e:
                    logger.warning(f"Failed to load global config from {config_path}: {e}")
        
        self._global_config = Config()
        return self._global_config
    
    def _load_config_file(self, path: Path) -> Config:
        """Load configuration from a file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = Config()
            
            if 'language_map' in data and isinstance(data['language_map'], dict):
                config.language_map = {
                    k: v for k, v in data['language_map'].items() 
                    if not k.startswith('#')
                }
            
            if 'filename_map' in data and isinstance(data['filename_map'], dict):
                config.filename_map = {
                    k: v for k, v in data['filename_map'].items() 
                    if not k.startswith('#')
                }
            
            if 'text_extensions' in data and isinstance(data['text_extensions'], list):
                config.text_extensions = set(
                    ext for ext in data['text_extensions'] if not ext.startswith('#')
                )
            
            if 'ignore_patterns' in data and isinstance(data['ignore_patterns'], list):
                config.ignore_patterns = [
                    pattern for pattern in data['ignore_patterns'] 
                    if not pattern.startswith('#')
                ]
            
            if 'default_language' in data and isinstance(data['default_language'], str):
                config.default_language = data['default_language']
            
            return config
            
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load config from {path}: {e}")
            return Config()
    
    def _load_legacy_ignore_file(self, directory: Path) -> List[str]:
        """Load ignore patterns from legacy context.ignore file"""
        ignore_file = directory / self.LEGACY_IGNORE_FILE
        patterns = []
        
        if ignore_file.exists():
            try:
                with open(ignore_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
                logger.debug(f"Loaded {len(patterns)} patterns from {ignore_file}")
            except Exception as e:
                logger.warning(f"Failed to load legacy ignore file {ignore_file}: {e}")
        
        return patterns
    
    def get_config_for_directory(self, directory: Path) -> Config:
        """Get the merged configuration for a specific directory"""
        directory = directory.resolve()
        
        if directory in self._cached_configs:
            return self._cached_configs[directory]
        
        merged_config = Config.get_default_config()
        global_config = self._load_global_config()
        merged_config = merged_config.merge(global_config)
        
        config_files = []
        current = directory
        try:
            while current != current.parent:
                config_file = current / self.DEFAULT_CONFIG_NAME
                if config_file.exists():
                    config_files.append(config_file)
                current = current.parent
        except RuntimeError:
            logger.warning(f"Path traversal terminated early for {directory}")
        
        for config_file in reversed(config_files):
            dir_config = self._load_config_file(config_file)
            merged_config = merged_config.merge(dir_config)
        
        legacy_patterns = self._load_legacy_ignore_file(directory)
        if legacy_patterns:
            legacy_config = Config(ignore_patterns=legacy_patterns)
            merged_config = merged_config.merge(legacy_config)
        
        # Cache the merged config for future use
        self._cached_configs[directory] = merged_config
        return merged_config
    
    def create_example_config(self, path: Path) -> bool:
        """Create an example configuration file
        
        Returns:
            bool: True if config was created successfully, False otherwise
        """
        example_config = {
            "language_map": {
                ".custom": "custom-language",
                ".myext": "mylang",
                "# Add more extension mappings here": "..."
            },
            "filename_map": {
                "customfile": "custom-language",
                "configfile": "yaml",
                "# Add more filename mappings here": "..."
            },
            "text_extensions": [
                ".custom",
                ".myext",
                "# Add more extensions here"
            ],
            "ignore_patterns": [
                "# Common directories to ignore",
                "node_modules/",
                "dist/",
                "build/",
                "__pycache__/",
                ".git/",
                ".venv/",
                "venv/",
                
                "# Common files to ignore",
                "*.pyc",
                "*.min.js",
                "*.min.css",
                ".DS_Store",
                
                "# Add more patterns here"
            ],
            "default_language": "text"
        }
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(example_config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error creating example config at {path}: {e}")
            return False
    
    def clear_cache(self) -> None:
        """Clear the configuration cache"""
        self._cached_configs.clear()
        self._global_config = None