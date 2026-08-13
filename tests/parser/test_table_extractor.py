import unittest
from src.parser.table_extractor import TableExtractor

class TestTableExtractor(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = TableExtractor()

    def test_extract_markdown_table(self) -> None:
        text = (
            "Prefix text\n"
            "| Header 1 | Header 2 |\n"
            "| -------- | -------- |\n"
            "| Data 1   | Data 2   |\n"
            "Suffix text"
        )
        # Toạ độ giả định của khối table (giống output từ TableDetector)
        start = text.find("| Header 1")
        end = text.find("Suffix text")
        
        table = self.extractor.extract(text, (start, end), page_number=2)
        
        # Verify Dataclass fields
        self.assertEqual(table.page_number, 2)
        self.assertEqual(len(table.headers), 2)
        self.assertEqual(table.headers[0], "Header 1")
        self.assertEqual(table.headers[1], "Header 2")
        self.assertEqual(len(table.rows), 1)
        self.assertEqual(table.rows[0][0], "Data 1")
        self.assertEqual(table.rows[0][1], "Data 2")

    def test_extract_space_separated_table(self) -> None:
        text = (
            "Col1      Col2      Col3\n"
            "A         B         C\n"
            "1         2         3\n"
        )
        table = self.extractor.extract(text, (0, len(text)))
        
        self.assertEqual(len(table.headers), 3)
        self.assertEqual(table.headers[0], "Col1")
        self.assertEqual(len(table.rows), 2)
        self.assertEqual(table.rows[0][1], "B")
        self.assertEqual(table.rows[1][2], "3")

if __name__ == '__main__':
    unittest.main()
