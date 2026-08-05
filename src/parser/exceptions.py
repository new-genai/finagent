"""
Custom exceptions for the Dataset Parser module.
"""

class ParserError(Exception):
    """Base class for all parser exceptions."""
    pass

class DatasetNotFoundError(ParserError):
    """Raised when the target dataset or file is not found."""
    pass

class EncodingError(ParserError):
    """Raised when the file cannot be decoded."""
    pass

class MetadataError(ParserError):
    """Raised when metadata extraction fails."""
    pass

class InvalidReportError(ParserError):
    """Raised when the report content is invalid or unreadable."""
    pass
