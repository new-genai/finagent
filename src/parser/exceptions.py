class ParserError(Exception):
    """Base class for all parser exceptions."""
    pass

class EncodingError(ParserError):
    """Raised when there is an issue decoding the dataset."""
    pass

class DatasetNotFoundError(ParserError):
    """Raised when the dataset file or directory cannot be found."""
    pass

class InvalidReportError(ParserError):
    """Raised when the report structure is invalid or unparseable."""
    pass
