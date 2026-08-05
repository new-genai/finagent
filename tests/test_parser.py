import pytest
from pathlib import Path
from src.parser.parser import FinancialReportParser

def test_financial_report_parser(tmp_path):
    parser = FinancialReportParser()
    test_file = tmp_path / "VNM_financial_statements_2022_consolidated_extracted.txt"
    test_file.write_text("Report content\nLine 2\n<table></table>", encoding="utf-8")
    
    report = parser.parse(test_file)
    
    assert report.company == "VNM"
    assert report.year == 2022
    assert report.report_type == "consolidated"
    assert report.statistics.line_count == 3
    assert report.statistics.table_count == 1
    assert report.raw_text.startswith("Report content")
    assert report.to_json() is not None
