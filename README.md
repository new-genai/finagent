# Tài Liệu Thuyết Minh Sản Phẩm - R2AI Stage 2

## 1. Mô tả dữ liệu
- Dữ liệu sử dụng: BCTC dạng văn bản được cung cấp bởi Ban Tổ Chức (ViFinQA).
- Phương pháp trích xuất: Dữ liệu được parser bóc tách thành các bảng `.csv` lưu trong thư mục `data/`.
- Link truy cập dữ liệu (Google Drive): [ĐIỀN LINK CỦA BẠN VÀO ĐÂY]

## 2. Mô hình sử dụng
- LLM sử dụng: `Qwen/Qwen3-8B` (Thông qua OpenRouter API). Đây là mô hình mã nguồn mở, kích thước < 14B, tuân thủ hoàn toàn quy định của BTC.
- Checkpoint / Source model: Không fine-tune, sử dụng Zero-shot RAG Prompting.
- Link truy cập checkpoint: [ĐIỀN LINK NẾU CÓ, HOẶC XÓA DÒNG NÀY]

## 3. Cấu trúc mã nguồn
- Hệ thống áp dụng kiến trúc DAG (Directed Acyclic Graph) chia nhỏ truy vấn đa bước.
- Sử dụng Hybrid Retrieval: FAISS Vector Search + BM25 Lexical Search.
- Đóng gói code thành API sử dụng FastAPI.

## 4. Hướng dẫn sử dụng
B1: Cài đặt thư viện: `pip install -r requirements.txt`
B2: Khởi tạo database: `python scripts/rebuild_all.py`
B3: Chạy API: `python run_api.py`
B4: Tạo file submission: `python format_submission.py`
