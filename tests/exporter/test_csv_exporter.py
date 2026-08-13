import unittest
import tempfile
import csv
from pathlib import Path

from src.parser.models import FinancialReport, Page, Table, Metadata
from src.exporter.csv_exporter import CSVExporter

class TestCSVExporter(unittest.TestCase):
    def setUp(self) -> None:
        self.exporter = CSVExporter()
        
        # Tạo một thư mục tạm thời (chỉ tồn tại lúc chạy test)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.out_path = Path(self.temp_dir.name)
        
        # --- Tạo Mock Data (Dữ liệu giả lập theo đúng chuẩn Data Models) ---
        metadata = Metadata()
        metadata.additional_info = {"ticker": "FPT", "year": "2023"}
        
        table1 = Table(
            id="t1", 
            page_number=1, 
            headers=["Tài Sản", "Năm 2023", "Năm 2022"],
            rows=[
                ["Tiền mặt", "100", "80"], 
                ["Hàng kho", "200", "150"]
            ]
        )
        
        page1 = Page(page_number=1, content="", tables=[table1])
        
        self.report = FinancialReport(
            report_id="r1",
            metadata=metadata,
            pages=[page1],
            raw_content=""
        )

    def tearDown(self) -> None:
        # Xoá thư mục tạm sau khi test xong
        self.temp_dir.cleanup()

    def test_export_csv_creates_files(self) -> None:
        """Kiểm tra xem Exporter có tạo ra đúng file CSV với tên chuẩn không."""
        exported_files = self.exporter.export(self.report, self.out_path)
        
        self.assertEqual(len(exported_files), 1)
        
        file_path = exported_files[0]
        self.assertTrue(file_path.exists())
        self.assertEqual(file_path.name, "FPT_2023_page1_table1.csv")

    def test_csv_content_is_correct(self) -> None:
        """Kiểm tra xem nội dung bên trong file CSV có khớp với dữ liệu gốc không."""
        exported_files = self.exporter.export(self.report, self.out_path)
        file_path = exported_files[0]
        
        # Đọc ngược lại file CSV vừa sinh ra
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            # Tổng cộng phải có 3 dòng (1 header + 2 data rows)
            self.assertEqual(len(rows), 3) 
            self.assertEqual(rows[0], ["Tài Sản", "Năm 2023", "Năm 2022"])
            self.assertEqual(rows[1], ["Tiền mặt", "100", "80"])
            self.assertEqual(rows[2], ["Hàng kho", "200", "150"])

if __name__ == '__main__':
    unittest.main()
