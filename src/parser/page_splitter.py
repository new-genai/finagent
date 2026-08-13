from abc import ABC, abstractmethod
from typing import List

from .models import Page
from .utils import setup_logger

logger = setup_logger(__name__)

class PageSplitterStrategy(ABC):
    """
    Abstract Strategy for splitting text into Pages.
    All future splitting algorithms must implement this interface.
    """
    
    @abstractmethod
    def split(self, text: str) -> List[Page]:
        pass

class SinglePageSplitter(PageSplitterStrategy):
    """
    MVP Strategy: Treats the entire text as a single page.
    """
    
    def split(self, text: str) -> List[Page]:
        logger.debug("Splitting text using SinglePageSplitter (MVP)")
        if not text:
            logger.warning("Empty text provided to splitter.")
            return []
            
        page = Page(page_number=1, content=text)
        return [page]

class PageSplitter:
    """
    Context class that uses a splitting strategy.
    """
    
    def __init__(self, strategy: PageSplitterStrategy = None) -> None:
        # Default to MVP strategy if none provided
        self._strategy = strategy or SinglePageSplitter()
        
    def set_strategy(self, strategy: PageSplitterStrategy) -> None:
        """Allows dynamically changing the splitting strategy at runtime."""
        self._strategy = strategy
        
    def split_pages(self, text: str) -> List[Page]:
        """Executes the split using the currently configured strategy."""
        return self._strategy.split(text)
