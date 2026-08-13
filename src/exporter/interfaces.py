from abc import ABC, abstractmethod
from typing import Any
from pathlib import Path
from src.parser.models import FinancialReport

class Exporter(ABC):
    """
    Abstract Base Class for all Exporters.
    Định nghĩa một hợp đồng (Contract) bắt buộc mọi loại Exporter 
    (CSV, JSON, Excel, PDF...) phải tuân thủ.
    """
    
    @abstractmethod
    def export(self, report: FinancialReport, output_path: Path | str) -> Any:
        """
        Chuyển đổi FinancialReport sang định dạng mong muốn và lưu trữ.
        `output_path` có thể là một thư mục (Dir) hoặc một File tuỳ theo logic của Exporter.
        """
        pass
