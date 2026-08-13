import unittest
import tempfile
import csv
from pathlib import Path

from src.loader.duckdb_manager import DuckDBManager

class TestDuckDBManager(unittest.TestCase):
    def setUp(self) -> None:
        # Tạo thư mục ảo để chứa CSV
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)
        
        # Tạo file CSV số 1
        self.csv1 = self.data_dir / "VNM_2023_page1_table1.csv"
        with open(self.csv1, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Asset", "Value"])
            writer.writerow(["Cash", "1000"])
            writer.writerow(["Inventory", "5000"])
            
        # Tạo file CSV số 2
        self.csv2 = self.data_dir / "FPT_2023_page2_table1.csv"
        with open(self.csv2, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Revenue", "Profit"])
            writer.writerow(["15000", "3000"])
            
        # Khởi tạo DB trên RAM
        self.db = DuckDBManager(":memory:")

    def tearDown(self) -> None:
        self.db.close()
        self.temp_dir.cleanup()

    def test_load_and_query(self) -> None:
        # Bước 1: Load toàn bộ CSV trong folder vào DuckDB
        self.db.load(self.data_dir)
        
        # Bước 2: Thử truy vấn bảng thứ nhất (DuckDB tự ép kiểu Value thành số nguyên 1000)
        result1 = self.db.query('SELECT * FROM "VNM_2023_page1_table1"')
        self.assertEqual(len(result1), 2)
        self.assertEqual(result1[0], ("Cash", 1000))
        self.assertEqual(result1[1], ("Inventory", 5000))
        
        # Bước 3: Thử truy vấn bảng thứ hai (Chỉ lấy cột Profit)
        result2 = self.db.query('SELECT Profit FROM "FPT_2023_page2_table1"')
        self.assertEqual(len(result2), 1)
        self.assertEqual(result2[0], (3000,))

    def test_invalid_directory(self) -> None:
        # Kiểm tra xử lý lỗi khi nạp từ thư mục không tồn tại
        with self.assertRaises(ValueError):
            self.db.load("/invalid/path/that/does/not/exist")

if __name__ == '__main__':
    unittest.main()
