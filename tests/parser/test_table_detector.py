import unittest
from src.parser.table_detector import TableDetector

class TestTableDetector(unittest.TestCase):
    def setUp(self) -> None:
        self.detector = TableDetector()

    def test_detect_markdown_table(self) -> None:
        text = (
            "Here is some text.\n"
            "| Header 1 | Header 2 |\n"
            "| -------- | -------- |\n"
            "| Data 1   | Data 2   |\n"
            "More text."
        )
        locations = self.detector.detect(text)
        self.assertEqual(len(locations), 1)
        
        start, end = locations[0]
        table_text = text[start:end]
        self.assertIn("Header 1", table_text)
        self.assertIn("Data 1", table_text)

    def test_detect_space_separated_table(self) -> None:
        text = (
            "Financial Results:\n\n"
            "Revenue         1000    2000\n"
            "Expenses        500     800\n"
            "Net Profit      500     1200\n\n"
            "End of report."
        )
        locations = self.detector.detect(text)
        self.assertEqual(len(locations), 1)
        
        start, end = locations[0]
        table_text = text[start:end]
        self.assertIn("Revenue", table_text)
        self.assertIn("Net Profit", table_text)

    def test_no_table(self) -> None:
        text = (
            "This is just a normal paragraph.\n"
            "It has no tables inside it.\n"
            "Even if it has a single line with   spaces, it's not a table unless it spans multiple lines."
        )
        locations = self.detector.detect(text)
        self.assertEqual(len(locations), 0)

    def test_multiple_tables(self) -> None:
        text = (
            "Table 1:\n"
            "A   B\n"
            "1   2\n"
            "\n"
            "Table 2:\n"
            "C   D\n"
            "3   4\n"
        )
        locations = self.detector.detect(text)
        self.assertEqual(len(locations), 2)

if __name__ == '__main__':
    unittest.main()
