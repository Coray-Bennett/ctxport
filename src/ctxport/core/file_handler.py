"""
File handling functionality for Code Context Exporter
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

from ctxport.config import Config

logger = logging.getLogger(__name__)


class FileHandler:
    """
    Handles reading and language detection for files.
    """
    
    def __init__(self, config: Config, base_directory: Path):
        """
        Initialize the file handler.
        
        Args:
            config: The configuration containing language mappings
            base_directory: The base directory for relative path calculation
        """
        self.config = config
        self.base_directory = base_directory.resolve()
    
    def get_relative_path(self, file_path: Path) -> Path:
        """
        Get the relative path from the base directory.
        
        Args:
            file_path: The absolute file path
            
        Returns:
            The path relative to the base directory
        """
        try:
            return file_path.relative_to(self.base_directory)
        except ValueError:
            # If we can't calculate relative path, return the file name
            return Path(file_path.name)
    
    def read_file(self, file_path: Path) -> Tuple[str, Optional[str]]:
        """
        Read a file and determine its language.
        
        Args:
            file_path: The file path to read
            
        Returns:
            A tuple of (file_content, language)
        """
        language = self.get_language(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content, language
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                return content, language
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                return f"# Error reading file: {str(e)}", language
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return f"# Error reading file: {str(e)}", language
    
    def get_language(self, file_path: Path) -> Optional[str]:
        """
        Determine the language for syntax highlighting based on filename or extension.
        
        Args:
            file_path: The file path to check
            
        Returns:
            The language identifier or None if not determined
        """
        # First check filename mapping (case-insensitive)
        filename = file_path.name.lower()
        if filename in self.config.filename_map:
            return self.config.filename_map[filename]
        
        # Then check extension mapping
        ext = file_path.suffix.lower() 
        return self.config.language_map.get(ext, self.config.default_language)