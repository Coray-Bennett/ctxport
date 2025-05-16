"""
Base formatter interface
"""

from abc import ABC, abstractmethod
from typing import Optional


class OutputFormatter(ABC):
    """
    Abstract base class for output formatters.
    
    Formatters convert the exported code into a specific output format.
    """
    
    @abstractmethod
    def begin_document(self, project_name: str) -> None:
        """
        Begin a new document.
        
        Args:
            project_name: The name of the project being exported
        """
        pass
    
    @abstractmethod
    def add_file(self, path: str, content: str, language: Optional[str] = None) -> None:
        """
        Add a file to the document.
        
        Args:
            path: The relative path of the file
            content: The content of the file
            language: The language identifier for syntax highlighting (optional)
        """
        pass
    
    @abstractmethod
    def add_error(self, message: str) -> None:
        """
        Add an error message to the document.
        
        Args:
            message: The error message
        """
        pass
    
    @abstractmethod
    def end_document(self) -> str:
        """
        Finalize and return the document.
        
        Returns:
            The formatted document as a string
        """
        pass