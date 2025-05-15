"""
MIME type utility functions for Code Context Exporter
"""

import logging
import mimetypes
from pathlib import Path

logger = logging.getLogger(__name__)

# Make sure mimetype database is initialized
mimetypes.init()


def is_text_file(file_path: Path) -> bool:
    """
    Check if a file is a text file using mime type detection and fallback methods.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file is a text file, False otherwise
    """
    # First try mime type detection
    try:
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and mime_type.startswith('text/'):
            return True
    except Exception as e:
        logger.debug(f"Error guessing MIME type for {file_path}: {e}")
    
    # Then try to read the file as text
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Try to read the first few KB
            f.read(4096)
        return True
    except UnicodeDecodeError:
        # Not a UTF-8 text file, try another common encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                f.read(4096)
            return True
        except Exception:
            return False
    except (IOError, PermissionError):
        return False