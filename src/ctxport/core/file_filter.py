"""
File filtering functionality
"""

import fnmatch
import logging
from pathlib import Path

from ctxport.config import Config
from ctxport.utils.mime_utils import is_text_file

logger = logging.getLogger(__name__)


class FileFilter:
    """
    Handles filtering of files based on configuration rules.
    """
    
    def __init__(self, config: Config, base_directory: Path):
        """
        Initialize the file filter.
        
        Args:
            config: The configuration containing ignore patterns and text extensions
            base_directory: The base directory for relative path calculation
        """
        self.config = config
        self.base_directory = base_directory.resolve()
        self._always_ignore_files = {'.ctxport.json', 'ctxport.json', 'context.ignore'}
    
    def should_include_file(self, file_path: Path) -> bool:
        """
        Determines whether a file should be included in the export.
        
        Args:
            file_path: The file path to check
            
        Returns:
            True if the file should be included, False otherwise
        """
        # Skip if it should be ignored
        if self.should_ignore(file_path):
            return False
            
        # Skip if it's not a text file
        if not self.is_text_file(file_path):
            return False
            
        return True
    
    def should_ignore(self, file_path: Path) -> bool:
        """
        Check if a file should be ignored based on ignore patterns.
        
        Args:
            file_path: The file path to check
            
        Returns:
            True if the file should be ignored, False otherwise
        """
        # Skip non-files
        if not file_path.is_file():
            return True
            
        # Always ignore our configuration files
        if file_path.name in self._always_ignore_files:
            return True
            
        try:
            # Calculate the relative path from the base directory
            relative_path = file_path.relative_to(self.base_directory)
            
            # Check each ignore pattern
            for pattern in self.config.ignore_patterns:
                # Handle directory patterns that end with '/'
                if pattern.endswith('/'):
                    dir_pattern = pattern[:-1]
                    if any(part == dir_pattern for part in relative_path.parts):
                        logger.debug(f"Ignoring {relative_path} (matched directory pattern: {pattern})")
                        return True
                
                # Check if pattern matches the full relative path
                if fnmatch.fnmatch(str(relative_path), pattern):
                    logger.debug(f"Ignoring {relative_path} (matched pattern: {pattern})")
                    return True
                    
                # Check if pattern matches any part of the path
                for part in relative_path.parts:
                    if fnmatch.fnmatch(part, pattern):
                        logger.debug(f"Ignoring {relative_path} (matched pattern part: {pattern})")
                        return True
        except ValueError:
            # If we can't calculate relative path, ignore the file
            return True
            
        return False
    
    def is_text_file(self, file_path: Path) -> bool:
        """
        Determine if a file is a text file that should be included.
        
        Args:
            file_path: The file path to check
            
        Returns:
            True if the file is a text file, False otherwise
        """
        # Check if the extension is in our configured text extensions
        if file_path.suffix.lower() in self.config.text_extensions:
            return True
            
        # Check if the filename is in our configured filename map
        if file_path.name.lower() in self.config.filename_map:
            return True
            
        # Use MIME type detection as a fallback
        try:
            return is_text_file(file_path)
        except Exception as e:
            logger.warning(f"Error checking if {file_path} is text: {e}")
            return False