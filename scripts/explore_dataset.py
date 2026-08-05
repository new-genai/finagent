"""
Dataset Explorer Script for ViFinQA Dataset.

Script này dùng để khảo sát Dataset.
Không parse.
Không tạo metadata.
Không tạo CSV.
"""

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any, Tuple

if sys.stdout.encoding.lower() != 'utf-8':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.progress import Progress
from rich.rule import Rule

console = Console()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Explore ViFinQA Dataset")
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/raw/ViFinQA",
        help="Đường dẫn đến thư mục chứa dataset",
    )
    return parser.parse_args()


def check_dataset_exists(dataset_path: Path) -> bool:
    """Kiểm tra dataset có tồn tại không."""
    if not dataset_path.exists():
        console.print(
            Panel(
                f"[bold red]Lỗi:[/bold red] Không tìm thấy dataset tại {dataset_path}",
                title="Lỗi",
                border_style="red",
            )
        )
        return False
    return True


def display_directory_structure(path: Path) -> None:
    """Hiển thị cấu trúc thư mục (mẫu) sử dụng Rich Tree."""
    tree = Tree(f"[bold blue]{path.name}[/bold blue]")

    # Lấy các mục ở level 1
    items = sorted(path.iterdir())
    for item in items:
        if item.is_dir():
            branch = tree.add(f"[bold cyan]{item.name}[/bold cyan]")
            # Lấy mẫu tối đa 3 phần tử con để tránh in ra màn hình quá dài
            children = sorted(item.iterdir())
            for child in children[:3]:
                if child.is_dir():
                    branch.add(f"[cyan]{child.name}[/cyan]")
                else:
                    branch.add(child.name)
            if len(children) > 3:
                branch.add("...")
        else:
            tree.add(item.name)

    console.print(Panel(tree, title="Cấu trúc thư mục", border_style="blue"))


def _extract_company_year(file_path: Path) -> Tuple[str, str]:
    """Trích xuất tên công ty và năm từ đường dẫn."""
    company = "Unknown"
    year = "Unknown"
    if "financial_statements" in file_path.parts:
        idx = file_path.parts.index("financial_statements")
        if len(file_path.parts) > idx + 2:
            company = file_path.parts[idx + 1]
            year = file_path.parts[idx + 2]
    return company, year


def gather_statistics(dataset_path: Path) -> Dict[str, Any]:
    """Khảo sát và thu thập thống kê về dataset."""
    stats = {
        "total_txt": 0,
        "total_json": 0,
        "total_dirs": 0,
        "reports_by_company": defaultdict(int),
        "reports_by_year": defaultdict(int),
        "total_lines": 0,
        "total_reports": 0,
        "txt_files": [],
        "encoding_errors": 0,
    }

    # Quét toàn bộ thư mục
    for p in dataset_path.rglob("*"):
        if p.is_dir():
            stats["total_dirs"] += 1
        elif p.suffix.lower() == ".txt":
            stats["total_txt"] += 1
            if "financial_statements" in p.parts:
                stats["txt_files"].append(p)
        elif p.suffix.lower() == ".json":
            stats["total_json"] += 1

    # Đọc các file TXT để tính dòng và check encoding
    with Progress() as progress:
        task = progress.add_task(
            "[cyan]Đang khảo sát các báo cáo...", total=len(stats["txt_files"])
        )

        for file_path in stats["txt_files"]:
            company, year = _extract_company_year(file_path)

            stats["reports_by_company"][company] += 1
            stats["reports_by_year"][year] += 1
            stats["total_reports"] += 1

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    stats["total_lines"] += len(lines)
            except UnicodeDecodeError:
                stats["encoding_errors"] += 1
            except Exception:
                pass
            finally:
                progress.advance(task)

    stats["total_companies"] = len(stats["reports_by_company"])
    stats["total_years"] = len(stats["reports_by_year"])
    return stats


def process_test_set(dataset_path: Path) -> Dict[str, Any]:
    """Đọc và thống kê file test.json (nếu có)."""
    test_json = dataset_path / "test.json"
    result: Dict[str, Any] = {}
    if test_json.exists():
        try:
            with open(test_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and data:
                    result["total_questions"] = len(data)

                    ids = []
                    for item in data:
                        item_id = item.get("id") or item.get("question_id")
                        if item_id is not None:
                            try:
                                ids.append(int(item_id))
                            except ValueError:
                                pass

                    if ids:
                        result["min_id"] = min(ids)
                        result["max_id"] = max(ids)

                    result["first_5"] = data[:5]
        except Exception as e:
            console.print(f"[yellow]Lỗi khi đọc test.json: {e}[/yellow]")
    return result


def sample_random_reports(txt_files: List[Path]) -> List[Dict[str, Any]]:
    """Lấy ngẫu nhiên 5 báo cáo và thu thập thông tin của chúng."""
    sample_reports = []
    if txt_files:
        samples = random.sample(txt_files, min(5, len(txt_files)))
        for p in samples:
            company, year = _extract_company_year(p)
            size = p.stat().st_size
            lines = 0
            try:
                with open(p, "r", encoding="utf-8") as f:
                    lines = sum(1 for _ in f)
            except UnicodeDecodeError:
                pass

            sample_reports.append(
                {
                    "name": p.name,
                    "company": company,
                    "year": year,
                    "size": size,
                    "lines": lines,
                }
            )
    return sample_reports


def export_summary(
    stats: Dict[str, Any], test_stats: Dict[str, Any], sample_reports: List[Dict[str, Any]]
) -> None:
    """Xuất báo cáo thống kê ra file Markdown."""
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Đảm bảo có .gitkeep
    gitkeep = reports_dir / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()

    summary_path = reports_dir / "dataset_summary.md"
    avg_lines = (
        stats.get("total_lines", 0) // stats.get("total_reports", 1)
        if stats.get("total_reports")
        else 0
    )

    lines = [
        "# Dataset Summary",
        "",
        "## Tổng quan",
        f"- **Tổng số công ty:** {stats.get('total_companies', 0)}",
        f"- **Tổng số năm:** {stats.get('total_years', 0)}",
        f"- **Tổng số báo cáo:** {stats.get('total_reports', 0)}",
        f"- **Tổng số file TXT:** {stats.get('total_txt', 0)}",
        f"- **Tổng số file JSON:** {stats.get('total_json', 0)}",
        f"- **Tổng số thư mục:** {stats.get('total_dirs', 0)}",
        f"- **Số dòng trung bình/báo cáo:** {avg_lines}",
        "",
        "## Thống kê",
        "",
        "### Theo công ty",
    ]

    for comp, count in sorted(stats.get("reports_by_company", {}).items()):
        lines.append(f"- **{comp}**: {count} báo cáo")

    lines.append("")
    lines.append("### Theo năm")
    for year, count in sorted(stats.get("reports_by_year", {}).items()):
        lines.append(f"- **{year}**: {count} báo cáo")

    lines.append("")
    lines.append("## Ví dụ báo cáo")
    for rep in sample_reports:
        lines.append(
            f"- File: `{rep['name']}` | Công ty: {rep['company']} | "
            f"Năm: {rep['year']} | Size: {rep['size']} bytes | Lines: {rep['lines']}"
        )

    lines.append("")
    lines.append("## Ví dụ câu hỏi")
    if test_stats:
        lines.append(f"- **Tổng số câu hỏi:** {test_stats.get('total_questions', 0)}")
        if "min_id" in test_stats:
            lines.append(f"- **ID nhỏ nhất:** {test_stats['min_id']}")
            lines.append(f"- **ID lớn nhất:** {test_stats['max_id']}")
        lines.append("")
        for q in test_stats.get("first_5", []):
            lines.append(f"```json\n{json.dumps(q, ensure_ascii=False, indent=2)}\n```")
    else:
        lines.append("*Không tìm thấy file test.json hoặc file không đúng định dạng.*")

    lines.append("")
    lines.append("## Ghi chú")
    if stats.get("encoding_errors", 0) > 0:
        lines.append(
            f"- **Cảnh báo:** Phát hiện {stats['encoding_errors']} báo cáo "
            f"bị lỗi Encoding (không phải UTF-8)."
        )
    else:
        lines.append("- Các báo cáo đều đọc được bằng chuẩn UTF-8.")

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    console.print(f"\n[bold green]Đã xuất báo cáo thành công tại: {summary_path}[/bold green]")


def display_stats_console(
    stats: Dict[str, Any], test_stats: Dict[str, Any], sample_reports: List[Dict[str, Any]]
) -> None:
    """Hiển thị thống kê ra màn hình console bằng Rich."""
    console.print(Rule("Thống Kê Tổng Quan", style="bold magenta"))

    table = Table(show_header=True, header_style="bold green")
    table.add_column("Loại")
    table.add_column("Số lượng", justify="right")

    table.add_row("Công ty", str(stats.get("total_companies", 0)))
    table.add_row("Năm", str(stats.get("total_years", 0)))
    table.add_row("Báo cáo (TXT)", str(stats.get("total_reports", 0)))
    table.add_row("Tổng file TXT", str(stats.get("total_txt", 0)))
    table.add_row("Tổng file JSON", str(stats.get("total_json", 0)))
    table.add_row("Thư mục", str(stats.get("total_dirs", 0)))

    avg_lines = (
        stats.get("total_lines", 0) // stats.get("total_reports", 1)
        if stats.get("total_reports")
        else 0
    )
    table.add_row("Số dòng TB/báo cáo", str(avg_lines))

    console.print(table)

    # By company (Top 10 to avoid too long output)
    console.print(Rule("Thống Kê Theo Công Ty (Hiển thị Top 10)", style="bold magenta"))
    comp_table = Table(show_header=True, header_style="bold blue")
    comp_table.add_column("Công ty")
    comp_table.add_column("Số báo cáo", justify="right")
    
    # Sort by count desc
    sorted_comps = sorted(
        stats.get("reports_by_company", {}).items(), key=lambda x: x[1], reverse=True
    )
    for comp, count in sorted_comps[:10]:
        comp_table.add_row(comp, str(count))
    console.print(comp_table)

    # By year
    console.print(Rule("Thống Kê Theo Năm", style="bold magenta"))
    year_table = Table(show_header=True, header_style="bold blue")
    year_table.add_column("Năm")
    year_table.add_column("Số báo cáo", justify="right")
    for year, count in sorted(stats.get("reports_by_year", {}).items()):
        year_table.add_row(str(year), str(count))
    console.print(year_table)

    if stats.get("encoding_errors", 0) > 0:
        console.print(
            Panel(
                f"[bold red]Cảnh báo:[/bold red] Có {stats['encoding_errors']} "
                f"file lỗi encoding khi đọc bằng UTF-8.",
                border_style="red",
            )
        )

    console.print(Rule("Ví dụ 5 Báo cáo", style="bold magenta"))
    rep_table = Table(show_header=True, header_style="bold yellow")
    rep_table.add_column("File")
    rep_table.add_column("Công ty")
    rep_table.add_column("Năm")
    rep_table.add_column("Size (Bytes)", justify="right")
    rep_table.add_column("Lines", justify="right")

    for rep in sample_reports:
        rep_table.add_row(
            rep["name"], rep["company"], rep["year"], str(rep["size"]), str(rep["lines"])
        )
    console.print(rep_table)


def main() -> None:
    """Hàm chạy chính."""
    args = parse_args()
    dataset_path = Path(args.dataset)

    if not check_dataset_exists(dataset_path):
        return

    display_directory_structure(dataset_path)

    stats = gather_statistics(dataset_path)

    txt_files = stats.get("txt_files", [])
    sample_reports = sample_random_reports(txt_files)
    test_stats = process_test_set(dataset_path)

    display_stats_console(stats, test_stats, sample_reports)

    export_summary(stats, test_stats, sample_reports)


if __name__ == "__main__":
    main()
