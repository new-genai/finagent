from abc import ABC, abstractmethod
from typing import Any
from pathlib import Path
from .models import FinancialReport

class Parser(ABC):
    """Abstract interface for all report parsers."""

    @abstractmethod
    def parse(self, file_path: Path | str) -> FinancialReport:
        """Main method to parse a file into a FinancialReport."""
        pass
