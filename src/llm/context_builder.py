import logging
from typing import List, Any
import pandas as pd
from src.schemas.core import RetrievedTable

logger = logging.getLogger(__name__)

class ContextBuilder:
    def __init__(self, table_loader: Any = None, **kwargs):
        self.table_loader = table_loader

    def _get_top_relevant_rows_fast(self, df: pd.DataFrame, metric_intent: str, top_n: int = 5) -> pd.DataFrame:
        if df.empty or not metric_intent:
            return df.head(top_n)
            
        intent_lower = metric_intent.lower()
        # BỎ ĐIỀU KIỆN len(w) > 2
        keywords = [w for w in intent_lower.split() if len(w) > 0]
        
        if not keywords:
            return df.head(top_n)
            
        def score_row(row):
            row_str = " ".join([str(val).lower() for val in row.values if pd.notna(val)])
            score = sum(1 for k in keywords if k in row_str)
            if "doanh thu" in row_str: score += 50
            if "lợi nhuận" in row_str or "lnst" in row_str: score += 50
            if "sau thuế" in row_str: score += 50
            if "tài sản" in row_str or "nguồn vốn" in row_str: score += 50
            if "nợ" in row_str: score += 50
            return score
            
        scores = df.apply(score_row, axis=1)
        if scores.max() == 0:
            return df.head(top_n)
            
        top_indices = scores.nlargest(top_n).index
        return df.loc[top_indices]

    def build(self, tables: List[RetrievedTable], metric_intent: str = '') -> str:
        if not tables:
            return 'Khong co bang du lieu nao.'
            
        context_lines = []
        for t in tables:
            t_id = getattr(t, 'table_id', 'unknown')
            comp = getattr(t, 'company', 'unknown')
            year = getattr(t, 'year', 'unknown')
            cols = getattr(t, 'columns', [])
            
            header_info = f"- BẢNG dfs['{t_id}'] | Cong ty {comp} ({year}) | Cot: {' | '.join(cols)}"
            df = getattr(t, 'dataframe', None)
            
            if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
                dtypes_str = ', '.join([f"'{c}': {dtype}" for c, dtype in df.dtypes.items()])
                schema_info = f"Schema: {{ {dtypes_str} }}"
                top_df = self._get_top_relevant_rows_fast(df, metric_intent, top_n=5)
                try:
                    sample_data = top_df.to_markdown(index=True)
                except Exception:
                    sample_data = top_df.to_string(index=True)
            else:
                schema_info = 'Schema: Empty'
                sample_data = '(Bang rong)'
                
            context_lines.append(f"{header_info}\n  {schema_info}\n  [TOP DONG LIEN QUAN]:\n{sample_data}\n")
            
        return '\n'.join(context_lines)
