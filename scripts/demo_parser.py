import os
import sys
import io
from pathlib import Path

# Force UTF-8 for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Đảm bảo Python hiểu thư mục gốc của project (thư mục chứa src) để import module
# Dòng code này tìm thư mục cha của thư mục chứa script hiện tại và đưa vào sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Import thư viện rich để hiển thị console UI đẹp mắt
from rich.console import Console
from rich.table import Table as RichTable
from rich.panel import Panel

# Import Parser đã xây dựng từ BƯỚC 1 -> 7
from src.parser import FinancialReportParser

def create_dummy_data() -> Path:
    """Hàm phụ trợ: Tạo một file txt giả lập để chạy demo."""
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True) # Tạo thư mục scripts/data nếu chưa có
    
    # Đặt tên file theo đúng chuẩn để MetadataExtractor lấy được dữ liệu
    file_path = data_dir / "VNM_financial_statements_2023_audited.txt"
    
    # Tạo nội dung chứa 2 bảng: 1 bảng Markdown và 1 bảng bằng dấu cách
    content = (
        "Báo cáo tài chính kiểm toán năm 2023 của Vinamilk.\n\n"
        "Bảng Cân Đối Kế Toán:\n"
        "| Tài Sản | Năm 2023 | Năm 2022 |\n"
        "| ------- | -------- | -------- |\n"
        "| Tiền Mặt| 1000     | 800      |\n"
        "| Hàng Kho| 5000     | 4500     |\n\n"
        "Bảng Kết Quả Kinh Doanh:\n"
        "Doanh Thu         15000     14000\n"
        "Lợi Nhuận         3000      2800\n"
    )
    file_path.write_text(content, encoding="utf-8")
    return file_path

def main() -> None:
    # 1. Khởi tạo Console của Rich
    console = Console()
    console.print(Panel.fit("[bold green]BẮT ĐẦU CHẠY DEMO DATASET PARSER[/bold green]"))
    
    # 2. Tạo file dữ liệu mẫu
    file_path = create_dummy_data()
    console.print(f"[cyan]Đã tạo file dữ liệu mẫu tại:[/cyan] {file_path.name}")
    
    # 3. Khởi tạo đối tượng Builder của chúng ta
    parser = FinancialReportParser()
    
    try:
        console.print("[yellow]Đang tiến hành parse...[/yellow]")
        
        # 4. CHUỖI XỬ LÝ FLUENT INTERFACE
        # Pipeline 5 bước chảy trơn tru để ra được object `report`
        report = (
            parser
                .read(file_path)
                .extract_metadata()
                .split_pages()
                .detect_tables()
                .extract_tables()
                .build()
        )
        
        console.print("\n[bold blue]=== KẾT QUẢ PARSE ===[/bold blue]")
        
        # 5. Hiển thị Metadata
        meta = report.metadata.additional_info
        console.print(f"[bold]Tên công ty (Ticker):[/bold] {meta.get('ticker', 'N/A')}")
        console.print(f"[bold]Năm:[/bold] {meta.get('year', 'N/A')}")
        console.print(f"[bold]Loại báo cáo:[/bold] {meta.get('report_type', 'N/A')}")
        console.print(f"[bold]Số page:[/bold] {len(report.pages)}")
        
        # Đếm tổng số table nằm trong tất cả các pages
        total_tables = sum(len(page.tables) for page in report.pages)
        console.print(f"[bold]Số table:[/bold] {total_tables}\n")
        
        # 6. Hiển thị danh sách Table trực quan bằng `RichTable`
        console.print("[bold magenta]--- Chi tiết Danh sách Table ---[/bold magenta]")
        
        for page in report.pages:
            for i, table in enumerate(page.tables, 1):
                # Khởi tạo bảng UI của thư viện rich
                rich_table = RichTable(title=f"Table {i} (ID: {table.id[:8]}...)", show_lines=True)
                
                # Render Headers
                for header in table.headers:
                    rich_table.add_column(header, style="cyan", no_wrap=True)
                    
                # Render Rows
                for row in table.rows:
                    # Trick nhỏ: Nếu độ dài row bị thiếu so với header (do parse), thì chèn thêm khoảng trống để bảng không bị vỡ
                    padded_row = row + [""] * (len(table.headers) - len(row))
                    rich_table.add_row(*padded_row[:len(table.headers)])
                    
                # In bảng ra console
                console.print(rich_table)
                console.print()
                
    except Exception as e:
        console.print(f"[bold red]Lỗi trong quá trình parse: {e}[/bold red]")

if __name__ == "__main__":
    main()
