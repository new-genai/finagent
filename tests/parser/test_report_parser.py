import unittest
import tempfile
from pathlib import Path

from src.parser.report_parser import FinancialReportParser
from src.parser.exceptions import ParserError

class TestFinancialReportParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = FinancialReportParser()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_fluent_builder_pattern(self) -> None:
        # Create a dummy file with correct metadata format in filename
        file_path = self.temp_path / "AAA_financial_statements_2023_consolidated.txt"
        test_content = (
            "Annual Report for AAA 2023\n\n"
            "Here is a financial table:\n"
            "| Col 1 | Col 2 |\n"
            "| ----- | ----- |\n"
            "| Val 1 | Val 2 |\n"
            "End of report."
        )
        file_path.write_text(test_content, encoding="utf-8")
        
        # Fluent Interface Execution
        report = (
            self.parser
                .read(file_path)
                .split_pages()
                .detect_tables()
                .extract_tables()
                .extract_metadata()
                .build()
        )
        
        # Assertions for Core Entity creation
        self.assertIsNotNone(report.report_id)
        self.assertEqual(report.raw_content, test_content)
        
        # Metadata Check
        self.assertEqual(report.metadata.additional_info.get("ticker"), "AAA")
        self.assertEqual(report.metadata.additional_info.get("year"), "2023")
        
        # Pages Check
        self.assertEqual(len(report.pages), 1)
        self.assertEqual(report.pages[0].page_number, 1)
        
        # Tables Check
        self.assertEqual(len(report.pages[0].tables), 1)
        self.assertEqual(report.pages[0].tables[0].headers, ["Col 1", "Col 2"])
        self.assertEqual(report.pages[0].tables[0].rows[0], ["Val 1", "Val 2"])

    def test_state_management_errors(self) -> None:
        # Test calling split_pages before read
        with self.assertRaises(ParserError):
            self.parser.split_pages()
            
        # Test calling detect_tables before split_pages
        file_path = self.temp_path / "dummy.txt"
        file_path.write_text("Hello world", encoding="utf-8")
        self.parser.read(file_path)
        with self.assertRaises(ParserError):
            self.parser.detect_tables()

    def test_html_table_parsing(self) -> None:
        file_path = self.temp_path / "VNM_financial_statements_2023.txt"
        test_content = (
            "Báo cáo tài chính VNM 2023\n\n"
            "Danh sách thành viên HĐQT:\n"
            "<table>\n"
            "  <tr><td>Ông Nguyễn Hạnh Phúc</td><td>Chủ tịch</td></tr>\n"
            "  <tr><td>Bà Mai Kiều Liên</td><td>Thành viên</td></tr>\n"
            "</table>\n"
            "Kết thúc báo cáo."
        )
        file_path.write_text(test_content, encoding="utf-8")
        
        report = (
            self.parser
                .read(file_path)
                .split_pages()
                .detect_tables()
                .extract_tables()
                .build()
        )
        
        self.assertEqual(len(report.pages[0].tables), 1)
        table = report.pages[0].tables[0]
        self.assertEqual(table.headers, ["Ông Nguyễn Hạnh Phúc", "Chủ tịch"])
        self.assertEqual(table.rows, [["Bà Mai Kiều Liên", "Thành viên"]])

if __name__ == '__main__':
    unittest.main()

