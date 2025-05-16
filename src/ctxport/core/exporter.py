"""
Main exporter functionality
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

from ctxport.config import Config, ConfigManager
from ctxport.core.file_filter import FileFilter
from ctxport.core.file_handler import FileHandler
from ctxport.formatters import OutputFormatter, MarkdownFormatter
from ctxport.utils.path_utils import find_files

logger = logging.getLogger(__name__)


class CodeExporter:
    """
    Main class for code context export functionality
    """
    
    def __init__(
        self, 
        config_manager: ConfigManager,
        formatter: Optional[OutputFormatter] = None
    ):
        """
        Initialize the code exporter.
        
        Args:
            config_manager: The configuration manager to use
            formatter: The output formatter to use (default: MarkdownFormatter)
        """
        self.config_manager = config_manager
        self.formatter = formatter or MarkdownFormatter()
        self.directory: Optional[Path] = None
        self.config: Optional[Config] = None
        self.file_handler: Optional[FileHandler] = None
        self.file_filter: Optional[FileFilter] = None
    
    def set_directory(self, directory: Path) -> None:
        """
        Set the working directory and load appropriate config.
        
        Args:
            directory: The directory to export
        """
        self.directory = directory.resolve()
        self.config = self.config_manager.get_config_for_directory(self.directory)
        self.file_handler = FileHandler(self.config, self.directory)
        self.file_filter = FileFilter(self.config, self.directory)
        logger.debug(f"Set working directory to: {self.directory}")
    
    def export_directory(self, verbose: bool = False) -> Tuple[str, int]:
        """
        Export all files in the directory to the configured format.
        
        Args:
            verbose: Whether to print verbose output
            
        Returns:
            A tuple of (formatted_output, file_count)
        """
        if not self.directory or not self.config:
            raise RuntimeError("Working directory not set. Call set_directory() first.")
            
        self.formatter.begin_document(self.directory.name)
        file_count = 0
        
        try:
            for file_path in sorted(find_files(self.directory)):
                if not self.file_filter.should_include_file(file_path):
                    continue
                    
                if verbose:
                    rel_path = self.file_handler.get_relative_path(file_path)
                    logger.info(f"Processing: {rel_path}")
                
                self._process_file(file_path)
                file_count += 1
        except Exception as e:
            logger.error(f"Error during export: {e}")
            self.formatter.add_error(f"Error during export: {e}")
            
        output_content = self.formatter.end_document()
        
        return output_content, file_count
    
    def _process_file(self, file_path: Path) -> None:
        """
        Process a single file and add its content to the output.
        
        Args:
            file_path: The file path to process
        """
        relative_path = self.file_handler.get_relative_path(file_path)
        content, language = self.file_handler.read_file(file_path)
        
        self.formatter.add_file(
            path=str(relative_path),
            content=content,
            language=language
        )
        
    def set_formatter(self, formatter: OutputFormatter) -> None:
        """
        Set a different output formatter.
        
        Args:
            formatter: The formatter to use
        """
        self.formatter = formatter
