"""
Clipboard management functionality
"""

import logging
import platform
import subprocess

logger = logging.getLogger(__name__)


class ClipboardManager:
    """
    Handles copying text to the system clipboard across different platforms.
    """
    
    def copy_to_clipboard(self, text: str) -> bool:
        """
        Copy text to system clipboard.
        
        Args:
            text: The text to copy to clipboard
            
        Returns:
            True if successful, False otherwise
        """
        system = platform.system().lower()
        
        try:
            if system == 'darwin':  # macOS
                return self._copy_macos(text)
            elif system == 'linux':
                return self._copy_linux(text)
            elif system == 'windows':
                return self._copy_windows(text)
            else:
                logger.warning(f"Unsupported platform: {system}")
                return False
        except Exception as e:
            logger.error(f"Error copying to clipboard: {e}")
            return False
    
    def _copy_macos(self, text: str) -> bool:
        """
        Copy text to clipboard on macOS.
        
        Args:
            text: The text to copy
            
        Returns:
            True if successful, False otherwise
        """
        process = subprocess.Popen(
            'pbcopy', 
            env={'LANG': 'en_US.UTF-8'}, 
            stdin=subprocess.PIPE
        )
        process.communicate(text.encode('utf-8'))
        return process.returncode == 0
    
    def _copy_linux(self, text: str) -> bool:
        """
        Copy text to clipboard on Linux.
        
        Args:
            text: The text to copy
            
        Returns:
            True if successful, False otherwise
        """
        for clipboard_cmd in [
            ['xclip', '-selection', 'clipboard'],
            ['xsel', '--clipboard', '--input'],
            ['wl-copy'],  # Wayland support
        ]:
            try:
                process = subprocess.Popen(
                    clipboard_cmd,
                    stdin=subprocess.PIPE
                )
                process.communicate(text.encode('utf-8'))
                if process.returncode == 0:
                    return True
            except FileNotFoundError:
                # Tool not found, try next one
                continue
        
        logger.warning("No clipboard tool found on Linux. Install xclip, xsel, or wl-copy.")
        return False
    
    def _copy_windows(self, text: str) -> bool:
        """
        Copy text to clipboard on Windows.
        
        Args:
            text: The text to copy
            
        Returns:
            True if successful, False otherwise
        """
        process = subprocess.Popen(
            ['clip'],
            stdin=subprocess.PIPE,
            shell=True
        )
        process.communicate(text.encode('utf-8'))
        return process.returncode == 0