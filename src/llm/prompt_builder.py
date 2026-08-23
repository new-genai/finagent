import logging

logger = logging.getLogger(__name__)

class PromptBuilder:
    def build_data_aware_prompt(self, question: str, context_str: str, dfs: dict) -> str:
        # Trích xuất dữ liệu mẫu từ các DataFrame thực tế
        samples = []
        for t_id, df in dfs.items():
            head_md = df.head(3).to_markdown()
            samples.append(f"--- BẢNG dfs['{t_id}'] (Columns: {list(df.columns)}) ---\n{head_md}\n")
        
        sample_data_str = "\n".join(samples)
        
        return (
            f"Bạn là chuyên gia lập trình Pandas tài chính.\n"
            f"Câu hỏi: '{question}'\n\n"
            f"DỮ LIỆU MẪU THỰC TẾ (SAMPLE ROWS):\n{sample_data_str}\n\n"
            f"HƯỚNG DẪN:\n"
            f"1. Dựa vào dữ liệu mẫu phía trên, hãy chọn đúng tên cột và tên dòng.\n"
            f"2. Tuyệt đối KHÔNG dùng hàm .max() bừa bãi. Phải lọc đúng dòng chỉ tiêu.\n"
            f"3. Gán kết quả cuối cùng vào biến `result` (kiểu float).\n\n"
            f"Viết mã Python trong khối ```python ... ```."
        )

    def build_multi_calc_prompt(self, question: str, context_str: str) -> str:
        """Prompt tối ưu cho bài toán tính toán liên bảng (Câu 2)."""
        return (
            f"Bạn là chuyên gia lập trình Python Pandas tính toán Báo cáo tài chính.\n"
            f"Câu hỏi: '{question}'\n\n"
            f"DANH SÁCH CÁC BẢNG DỮ LIỆU (`dfs` dictionary):\n{context_str}\n\n"
            f"HƯỚNG DẪN VIẾT CODE TÍNH TỔNG:\n"
            f"1. Duyệt qua từng DataFrame trong `dfs.values()`.\n"
            f"2. Với mỗi DataFrame, tìm cột năm tương ứng và lấy giá trị lớn nhất `.max()` của bảng đó.\n"
            f"3. Cộng dồn kết quả các bảng lại với nhau vào biến `result`.\n\n"
            f"VÍ DỤ MẪU CHUẨN:\n"
            f"```python\n"
            f"total_val = 0.0\n"
            f"for df in dfs.values():\n"
            f"    year_cols = [c for c in df.columns if '2023' in str(c)]\n"
            f"    if year_cols:\n"
            f"        target_col = year_cols[0]\n"
            f"        val = df[target_col].dropna().astype(float).max()\n"
            f"        total_val += val\n"
            f"result = total_val\n"
            f"```\n\n"
            f"Chỉ trả về mã Python trong khối ```python ... ```."
        )

    def build_coder_prompt(self, question: str, context_str: str, mode: str = "single") -> str:
        if mode == "multi":
            return self.build_multi_calc_prompt(question, context_str)
        return self.build_single_lookup_prompt(question, context_str)

    def build_planner_prompt(self, question: str, context_str: str) -> str:
        return ""