import pytest
from pathlib import Path
from src.parser.reader import TXTReader
from src.parser.config import ParserConfig
from src.parser.exceptions import DatasetNotFoundError

def test_reader_file_not_found():
    config = ParserConfig()
    reader = TXTReader(config)
    with pytest.raises(DatasetNotFoundError):
        reader.read("non_existent_file.txt")

def test_reader_success(tmp_path):
    config = ParserConfig()
    reader = TXTReader(config)
    test_file = tmp_path / "test_report.txt"
    test_file.write_text("Hello World", encoding="utf-8")
    
    content, enc = reader.read(test_file)
    assert content == "Hello World"
    assert enc == "utf-8"
