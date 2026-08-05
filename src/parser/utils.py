"""
Utility functions for the Dataset Parser module.
"""
import os

def format_size(size_bytes: int) -> str:
    """Format bytes to a human readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
