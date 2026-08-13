import unittest
from typing import List
from src.parser.page_splitter import PageSplitter, SinglePageSplitter, PageSplitterStrategy
from src.parser.models import Page

class TestPageSplitter(unittest.TestCase):
    def setUp(self) -> None:
        self.splitter = PageSplitter()

    def test_single_page_split(self) -> None:
        text = "This is the entire document content."
        pages = self.splitter.split_pages(text)
        
        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0].page_number, 1)
        self.assertEqual(pages[0].content, text)

    def test_empty_text_split(self) -> None:
        text = ""
        pages = self.splitter.split_pages(text)
        
        self.assertEqual(len(pages), 0)

    def test_strategy_pattern_switch(self) -> None:
        # Tạo một Strategy ảo (Mock Strategy) để test Pattern mà không sửa code chính
        class MockLineSplitter(PageSplitterStrategy):
            def split(self, text: str) -> List[Page]:
                lines = text.split('\n')
                return [Page(page_number=i+1, content=line) for i, line in enumerate(lines) if line]
                
        # Thay đổi vũ khí (Strategy) lúc runtime
        self.splitter.set_strategy(MockLineSplitter())
        
        text = "Line 1\nLine 2\nLine 3"
        pages = self.splitter.split_pages(text)
        
        self.assertEqual(len(pages), 3)
        self.assertEqual(pages[0].page_number, 1)
        self.assertEqual(pages[0].content, "Line 1")
        self.assertEqual(pages[2].page_number, 3)
        self.assertEqual(pages[2].content, "Line 3")

if __name__ == '__main__':
    unittest.main()
