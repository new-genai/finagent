"""
Configuration settings for the Dataset Parser module.
"""
from dataclasses import dataclass
from .constants import DEFAULT_ENCODING, FALLBACK_ENCODING

@dataclass
class ParserConfig:
    """Configuration for the FinancialReportParser."""
    dataset_root: str = "data/raw/ViFinQA"
    default_encoding: str = DEFAULT_ENCODING
    fallback_encoding: str = FALLBACK_ENCODING
    enable_logging: bool = True
    strict_mode: bool = False
