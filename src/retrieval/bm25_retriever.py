import logging
import pickle
from pathlib import Path
from typing import List, Optional, Union
from src.schemas.core import RetrievedTable

logger = logging.getLogger(__name__)

class BM25Retriever:
    def __init__(self, index_path: Optional[Union[str, Path]] = None, *args, **kwargs):
        self.doc_store = []
        if index_path:
            self.load(index_path)

    def load(self, path: Union[str, Path]):
        p = Path(path)
        if not p.exists(): return self
        try:
            with open(p, 'rb') as f:
                data = pickle.load(f)
                self.doc_store = data.get('doc_store', []) if isinstance(data, dict) else data
        except Exception as e:
            logger.error(f'Loi load index: {e}')
        return self

    def retrieve(self, query: str, company: Optional[str] = None, year: Optional[str] = None, top_k: int = 25) -> List[RetrievedTable]:
        if not self.doc_store: return []
        norm_company = company.upper().strip() if company else ''
        norm_year = str(year).strip() if year else ''
        q_lower = query.lower()
        
        is_kqkd = any(k in q_lower for k in ['doanh thu', 'loi nhuan', 'lợi nhuận', 'lnst'])
        is_cdkt = any(k in q_lower for k in ['tai san', 'tài sản', 'nguon von', 'nguồn vốn', 'no', 'nợ', 'von chu'])
        prefer_consolidated = 'rieng' not in q_lower and 'riêng' not in q_lower and 'me' not in q_lower and 'mẹ' not in q_lower

        scored = []
        for doc in self.doc_store:
            c = str(doc.get('company', '')).upper().strip()
            y = str(doc.get('year', '')).strip()
            cat = str(doc.get('table_category', '')).upper()
            rep = str(doc.get('report_type', '')).lower()
            
            if norm_company and c and c != norm_company: continue
            if norm_year and y and y != norm_year: continue
            
            score = 0.0
            doc_text = ' '.join([str(v).lower() for v in doc.get('keywords', []) + doc.get('headers', [])])
            
            if is_kqkd and ('KẾT QUẢ' in cat or 'KET QUA' in cat or 'KINH DOANH' in cat): score += 10000.0
            if is_cdkt and ('CÂN ĐỐI' in cat or 'CAN DOI' in cat or 'B NG C' in cat): score += 10000.0
            
            if prefer_consolidated and 'consolidated' in rep: score += 5000.0
            elif not prefer_consolidated and 'separate' in rep: score += 5000.0
                
            for w in q_lower.split():
                if len(w) > 1 and w in doc_text:
                    score += doc_text.count(w) * 2.0
                    
            if score > 0:
                scored.append((score, doc))
                
        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        # Ép luôn trả về 25 bảng thay vì top_k được truyền vào
        for score, doc in scored[:25]:
            results.append(RetrievedTable(
                table_id=doc.get('table_id', 'unknown'),
                duckdb_table=doc.get('duckdb_table', ''),
                company=doc.get('company', 'unknown'),
                year=str(doc.get('year', 'unknown')),
                score=float(score),
                columns=[str(h) for h in doc.get('headers', [])]
            ))
        return results

    def retrieve_single(self, sub_query: str, company: Optional[str] = None, year: Optional[str] = None, top_k: int = 3) -> List[RetrievedTable]:
        # Cố tình gọi retrieve với top 25 để đảm bảo quét sạch bách data
        return self.retrieve(sub_query, company=company, year=year, top_k=25)
