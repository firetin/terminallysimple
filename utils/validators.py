"""
Input validation utilities
"""

from typing import Final
from constants import MAX_FILENAME_LENGTH

# Reserved Windows filenames
RESERVED_NAMES: Final[set[str]] = {
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
}

DANGEROUS_CHARS: Final[str] = '<>:"|?*\0'


def sanitize_filename(filename: str) -> str:
    """
    Sanitize and validate a filename to prevent security issues.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        A safe filename string
        
    Raises:
        ValueError: If the filename is invalid or dangerous
    """
    if not filename or not filename.strip():
        raise ValueError("Filename cannot be empty")
    
    filename = filename.strip()
    
    # Remove path separators to prevent directory traversal
    if '/' in filename or '\\' in filename:
        raise ValueError("Filename cannot contain path separators (/ or \\)")
    
    # Check for parent directory references
    if filename in ('.', '..') or filename.startswith('.'):
        raise ValueError("Filename cannot start with '.' or be a directory reference")
    
    # Remove dangerous characters and control characters
    for char in DANGEROUS_CHARS:
        if char in filename:
            raise ValueError(f"Filename cannot contain '{char}' character")
    
    # Check for non-printable characters
    if not all(c.isprintable() or c.isspace() for c in filename):
        raise ValueError("Filename contains invalid characters")
    
    # Check for Windows reserved names (case-insensitive)
    name_without_ext = filename.rsplit('.', 1)[0].upper()
    if name_without_ext in RESERVED_NAMES:
        raise ValueError(f"'{filename}' is a reserved system name")
    
    # Limit filename length (most filesystems support 255, but leave room for extension)
    if len(filename) > MAX_FILENAME_LENGTH:
        raise ValueError(f"Filename is too long (max {MAX_FILENAME_LENGTH} characters)")
    
    return filename
