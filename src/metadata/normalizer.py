import logging

logger = logging.getLogger(__name__)

class TermNormalizer:
    """Normalizes financial terms using a predefined dictionary."""
    
    def __init__(self):
        # Dictionary of synonyms mapping to a standardized key
        self.term_mapping = {
            "doanh thu thuần": "net_revenue",
            "revenue": "net_revenue",
            "net revenue": "net_revenue",
            "sales": "net_revenue",
            "doanh thu": "net_revenue",
            "lợi nhuận": "profit",
            "profit": "profit",
            "net profit": "profit",
            "lợi nhuận sau thuế": "profit",
            "tài sản": "assets",
            "tổng tài sản": "assets",
            "assets": "assets",
            "tiền mặt": "cash",
            "cash": "cash",
            "hàng tồn kho": "inventory",
            "inventory": "inventory",
            "hàng kho": "inventory"
        }
        
    def normalize(self, term: str) -> str:
        """Normalizes a single term to its standard form. Returns lowercase term if not found."""
        if not term:
            return ""
        
        normalized = term.strip().lower()
        # Direct lookup
        if normalized in self.term_mapping:
            return self.term_mapping[normalized]
            
        # Substring matching (simple approach for MVP)
        for key, value in self.term_mapping.items():
            if key in normalized:
                return value
                
        return normalized
