"""
Demo script for the FinancialReportParser module.
"""
import sys
import argparse
from pathlib import Path

# Need this for Vietnamese encoding on Windows console
if sys.stdout.encoding.lower() != 'utf-8':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add src to python path so it can import it easily
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser import FinancialReportParser

console = Console()

def main():
    parser_args = argparse.ArgumentParser(description="Demo Dataset Parser")
    parser_args.add_argument(
        "--file",
        type=str,
        default="data/raw/ViFinQA/financial_statements/VSF/2019/VSF_financial_statements_2019_consolidated/VSF_financial_statements_2019_consolidated_extracted.txt",
        help="Đường dẫn đến file báo cáo để test"
    )
    args = parser_args.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        console.print(f"[red]Không tìm thấy file mặc định. Vui lòng truyền đường dẫn đúng bằng --file[/red]")
        return

    console.print(Panel(f"[bold cyan]Đang parse báo cáo:[/bold cyan] {file_path.name}"))
    
    parser = FinancialReportParser()
    try:
        report = parser.parse(file_path)
        
        # Display Metadata
        table = Table(title="Report Metadata", show_header=True, header_style="bold green")
        table.add_column("Thuộc tính")
        table.add_column("Giá trị")
        table.add_row("Report ID", report.report_id[:10] + "...")
        table.add_row("Company", report.company)
        table.add_row("Year", str(report.year))
        table.add_row("Type", report.report_type)
        table.add_row("Source", report.source_path)
        table.add_row("Encoding", report.encoding)
        console.print(table)
        
        # Display Statistics
        stats = Table(title="Report Statistics", show_header=True, header_style="bold yellow")
        stats.add_column("Thuộc tính")
        stats.add_column("Số lượng")
        stats.add_row("Ký tự (Characters)", str(report.statistics.character_count))
        stats.add_row("Dòng (Lines)", str(report.statistics.line_count))
        stats.add_row("Bảng (Tables - Heuristic)", str(report.statistics.table_count))
        console.print(stats)
        
        console.print("\n[bold green]Đã tạo thành công FinancialReport Object![/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Lỗi khi parse:[/bold red] {e}")

if __name__ == "__main__":
    main()
