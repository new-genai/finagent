import pytest
from pathlib import Path
from src.parser.metadata import MetadataExtractor

def test_metadata_extraction_regex():
    extractor = MetadataExtractor()
    path = Path("AAA_financial_statements_2023_consolidated_extracted.txt")
    metadata = extractor.extract(path)
    
    assert metadata.company == "AAA"
    assert metadata.year == 2023
    assert metadata.report_type == "consolidated"

def test_metadata_extraction_fallback():
    extractor = MetadataExtractor()
    path = Path("data/raw/ViFinQA/financial_statements/BBB/2021/BBB_financial_statements_2021_separate_extracted.txt")
    metadata = extractor.extract(path)
    
    assert metadata.company == "BBB"
    assert metadata.year == 2021
    assert metadata.report_type == "separate"
