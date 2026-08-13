from typing import List
from src.schemas.core import RetrievedTable

class ContextBuilder:
    """Xây dựng phần Context (dữ liệu các bảng) để nạp vào Prompt."""

    def build(self, tables: List[RetrievedTable]) -> str:
        """
        Chuyển đổi danh sách RetrievedTable thành chuỗi Text mô tả schema và dữ liệu mẫu.
        Giúp LLM hiểu được cấu trúc của các DataFrame được inject vào sandbox.
        """
        if not tables:
            return "Không có dữ liệu bảng nào được tìm thấy."

        context_str = "DỮ LIỆU ĐƯỢC CUNG CẤP (Nằm trong dict `dfs`):\n"
        context_str += "=" * 50 + "\n\n"

        for i, table in enumerate(tables, 1):
            context_str += f"Table Name: {table.table_id}\n"
            
            # Use dataframe to extract exact columns and preview
            if table.dataframe is not None and not table.dataframe.empty:
                columns = list(table.dataframe.columns)
                context_str += f"Columns: {columns}\n"
                
                # Convert the first 3 rows to markdown for preview
                preview = table.dataframe.head(3).to_markdown(index=False)
                context_str += f"Preview:\n{preview}\n\n"
            else:
                context_str += f"Columns: {table.columns}\n"
                context_str += "Preview: [Không có dữ liệu]\n\n"

        context_str += "=" * 50 + "\n"
        return context_str
