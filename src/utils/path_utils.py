"""
Path utility functions for Code Context Exporter
"""

import logging
import os
from pathlib import Path
from typing import Generator, List, Set

logger = logging.getLogger(__name__)


def find_files(directory: Path) -> Generator[Path, None, None]:
    """
    Recursively find all files in a directory.
    
    Args:
        directory: The directory to search
        
    Yields:
        Paths for all files in the directory
    """
    try:
        for item in directory.rglob("*"):
            if item.is_file():
                yield item
    except PermissionError as e:
        logger.warning(f"Permission error accessing {directory}: {e}")
    except Exception as e:
        logger.error(f"Error finding files in {directory}: {e}")


def safe_resolve(path: Path) -> Path:
    """
    Safely resolve a path, handling errors.
    
    Args:
        path: The path to resolve
        
    Returns:
        The resolved path or the original path if resolution fails
    """
    try:
        return path.resolve()
    except (OSError, RuntimeError) as e:
        logger.warning(f"Could not resolve {path}: {e}")
        return path


def normalize_path(path_str: str) -> Path:
    """
    Normalize a path string to a Path object.
    
    Args:
        path_str: String representation of a path
        
    Returns:
        Normalized Path object
    """
    # Expand user directory (tilde)
    expanded = os.path.expanduser(path_str)
    
    # Convert to absolute path
    if not os.path.isabs(expanded):
        expanded = os.path.abspath(expanded)
    
    # Return as Path object
    return safe_resolve(Path(expanded))
