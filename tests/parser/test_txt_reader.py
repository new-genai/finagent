import unittest
import tempfile
from pathlib import Path

from src.parser.txt_reader import TXTReader
from src.parser.exceptions import EncodingError, DatasetNotFoundError

class TestTXTReader(unittest.TestCase):
    def setUp(self) -> None:
        self.reader = TXTReader()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_read_utf8(self) -> None:
        file_path = self.temp_path / "test_utf8.txt"
        test_content = "Xin chào bằng UTF-8"
        file_path.write_text(test_content, encoding="utf-8")
        
        result = self.reader.read(file_path)
        self.assertEqual(result, test_content)

    def test_read_utf8_sig(self) -> None:
        file_path = self.temp_path / "test_utf8_sig.txt"
        test_content = "Xin chào bằng UTF-8-SIG"
        file_path.write_text(test_content, encoding="utf-8-sig")
        
        result = self.reader.read(file_path)
        self.assertEqual(result, test_content)

    def test_read_cp1258(self) -> None:
        file_path = self.temp_path / "test_cp1258.txt"
        test_content = "Xin chao CP1258"
        file_path.write_text(test_content, encoding="cp1258")
        
        result = self.reader.read(file_path)
        self.assertEqual(result, test_content)

    def test_file_not_found(self) -> None:
        file_path = self.temp_path / "nonexistent.txt"
        with self.assertRaises(DatasetNotFoundError):
            self.reader.read(file_path)

    def test_encoding_error(self) -> None:
        file_path = self.temp_path / "test_invalid.txt"
        # Ghi byte 0x81, byte này không hợp lệ trong utf-8 và không được định nghĩa trong cp1258
        file_path.write_bytes(b'\x81')
        
        with self.assertRaises(EncodingError):
            self.reader.read(file_path)

if __name__ == '__main__':
    unittest.main()
