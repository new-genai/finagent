# Tổng kết dự án End-to-End Financial QA và Nhiệm vụ tiếp theo

Chào Bình Minh, dưới đây là bản tóm tắt tiến độ dự án dựa trên kiến trúc End-to-End Financial QA (Text-to-Pandas). Mình (Hưng Nguyên) đã xây dựng xong nền tảng cơ bản, phần còn lại cần bạn tiếp quản và tối ưu thêm cho đúng với yêu cầu bài toán.

## 1. Phần việc Hưng Nguyên ĐÃ làm

- **Khung hệ thống Text-to-Pandas (PoT)**: Mình đã thiết lập thành công cơ chế Text-to-Pandas để hệ thống nhận câu hỏi, sinh mã Python/Pandas tương ứng và chạy sandbox để tính toán ra kết quả (ví dụ: tính tăng trưởng doanh thu). Hệ thống đang chạy ổn định hơn hẳn so với Text-to-SQL truyền thống trên dữ liệu bảng OCR phức tạp.
- **Tiền xử lý & Trích xuất Bảng**: Đã viết các script tiền xử lý, đọc dữ liệu từ PDF/HTML, làm sạch, chuẩn hóa tiêu đề và số liệu, sau đó lưu thành CSV. Mình cũng đã gán metadata (công ty, năm, loại báo cáo) vào từng bảng để LLM dễ đọc hơn.
- **Truy xuất Bảng biểu (Table Retrieval) - Cơ bản**: Đã dựng xong pipeline Retrieval kết hợp giữa lọc Metadata, Lexical Search (BM25) và Dense Retrieval (FAISS) để khoanh vùng top 50 bảng có khả năng chứa đáp án nhất.
- **Phân loại Intent**: Đã thiết lập xong luồng Intent Router thông minh để phân loại các câu hỏi giao tiếp thông thường với các truy vấn tài chính, giúp tiết kiệm chi phí gọi LLM tính toán.

---

## 2. Phần việc còn thiếu (Nhiệm vụ của Bình Minh)

Dưới đây là những điểm hệ thống hiện tại còn thiếu hụt so với chuẩn của bài toán Financial QA. Bình Minh đọc kỹ và giúp mình triển khai nhé:

### 2.1. Nâng cấp Pipeline Truy xuất (Tích hợp Reranker)
- **Vấn đề**: Hiện tại mình mới làm đến bước lấy ra Top 50 bảng đề cử. Theo bài báo, nếu thiếu hụt dù chỉ 1 "bảng vàng" thì toàn bộ quy trình QA multi-table sẽ nghẽn.
- **Việc cần làm**: Cần tích hợp thêm mô hình **Reranker** (như Qwen3-Embedding hoặc BGE) để chấm điểm lại Top 50 bảng đó, chọn ra đúng Top 10 bảng chứng cứ chính xác nhất, mục tiêu đưa recall@10 lên khoảng 80%.

### 2.2. Xử lý triệt để lỗi OCR (Cell Grounding)
- **Vấn đề**: Việc đọc sai ô dữ liệu chiếm tới 89.3% lỗi hệ thống. Thách thức lớn nhất của dữ liệu OCR là gộp ô, lệch hàng, tiêu đề lặp.
- **Việc cần làm**: Tinh chỉnh lại bộ Parser và thiết kế Prompt/Schema thật rõ ràng ở bước tiền xử lý để khắc phục các lỗi cấu trúc này, đảm bảo LLM định vị đúng ô dữ liệu (Cell Grounding).

### 2.3. Hỗ trợ chiến lược lai (Hybrid PoT & CoT)
- **Vấn đề**: Hiện tại mình chỉ mới dùng duy nhất PoT (sinh code Pandas). Các mô hình nhỏ thường xuyên bị lỗi cú pháp khi sinh code.
- **Việc cần làm**: Xây dựng cơ chế fallback sử dụng **Chain-of-Thought (CoT)** suy luận bằng văn bản tự nhiên dành riêng cho các câu hỏi dễ hoặc khi mô hình nhỏ gặp lỗi code crash.

### 2.4. Triển khai Mô hình Hợp tác Đa vai trò (Multi-Agent Collaboration)
- **Vấn đề**: Hiện tại luồng xử lý đang dồn hết cho 1 Agent duy nhất, dẫn đến sai sót khi chọn ô dữ liệu.
- **Việc cần làm**: Chia hệ thống thành 3 Agent độc lập:
  1. **Planner/Expert Agent**: Đọc câu hỏi, phân tích, định vị ô và lập kế hoạch.
  2. **Coder Agent**: (Phần này mình đã làm nền tảng) Mã hóa kế hoạch thành Pandas.
  3. **Auditor Agent**: Kiểm tra chéo kết quả của Coder, rà soát đơn vị, số liệu và loại bỏ ảo giác (hallucination) trước khi chốt câu trả lời cuối cùng.

### 2.5. Tối ưu Chuẩn hóa số liệu Việt Nam
- **Việc cần làm**: Cải thiện thêm khâu làm sạch để xử lý triệt để các định dạng số Việt Nam (dấu `.` và `,`, số âm trong ngoặc) ngay từ khâu parse thành DataFrame, giúp Coder sinh code tính toán dễ dàng hơn.
