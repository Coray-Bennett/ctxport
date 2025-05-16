"""
Markdown formatter
"""

from typing import List, Optional

from ctxport.formatters.base import OutputFormatter


class MarkdownFormatter(OutputFormatter):
    """
    Formats code context as markdown.
    
    The output includes a header with the project name,
    and each file in a section with its relative path in a code block
    with appropriate syntax highlighting.
    """
    
    def __init__(self):
        self.lines: List[str] = []
    
    def begin_document(self, project_name: str) -> None:
        """
        Begin a new markdown document.
        
        Args:
            project_name: The name of the project being exported
        """
        self.lines = [
            f"# Code Context Export: {project_name}",
            "",
        ]
    
    def add_file(self, path: str, content: str, language: Optional[str] = None) -> None:
        """
        Add a file to the markdown document.
        
        Args:
            path: The relative path of the file
            content: The content of the file
            language: The language identifier for syntax highlighting (optional)
        """
        self.lines.append(f"## {path}")
        self.lines.append("")
        
        lang_spec = language if language else ""
        self.lines.append(f"```{lang_spec}")
        self.lines.append(content)
        self.lines.append("```")
        self.lines.append("")
    
    def add_error(self, message: str) -> None:
        """
        Add an error message to the markdown document.
        
        Args:
            message: The error message
        """
        self.lines.append(f"### Error")
        self.lines.append("")
        self.lines.append(f"```")
        self.lines.append(message)
        self.lines.append("```")
        self.lines.append("")
    
    def end_document(self) -> str:
        """
        Finalize and return the markdown document.
        
        Returns:
            The formatted markdown document as a string
        """
        return "\n".join(self.lines)