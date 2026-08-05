# Hướng dẫn Cài đặt & Chạy dự án (Onboarding)

## 1. Giới thiệu
Chào mừng bạn gia nhập đội ngũ **NewGenAI**! 

Tài liệu này được soạn thảo nhằm mục đích giúp các thành viên mới (Onboarding) dễ dàng thiết lập môi trường phát triển trên máy cá nhân. Bằng cách làm theo từng bước dưới đây, bạn sẽ có thể clone mã nguồn, cài đặt môi trường, tải dữ liệu, và chạy thành công cả Frontend lẫn Backend của dự án **NewGenAI Financial Agent** một cách nhanh chóng nhất.

---

## 2. Yêu cầu hệ thống (Prerequisites)
Đảm bảo máy tính của bạn đã cài đặt sẵn các công cụ sau trước khi bắt đầu:
- **Git**
- **Git LFS** (Git Large File Storage - bắt buộc để quản lý các file model hoặc dataset nặng)
- **Python >= 3.12**
- **Node.js >= 20** (bắt buộc cho Next.js 15)
- **npm** (đã được chốt làm package manager chính, sử dụng chung file `package-lock.json`)

---

## 3. Clone Repository
Mở terminal và tải mã nguồn dự án về máy:

```bash
git clone https://github.com/new-genai/finagent.git
cd finagent

# Cài đặt và kích hoạt Git LFS trong repository này
git lfs install
git lfs pull
```

---

## 4. Thiết lập Môi trường Backend (Python)
Hệ thống xử lý chính (AI, Retrieval, Text-to-Pandas) chạy hoàn toàn trên Python. Chúng tôi bắt buộc sử dụng **môi trường ảo (virtual environment)** để tránh xung đột thư viện.

### Tạo và kích hoạt môi trường ảo
```bash
# Tạo môi trường ảo có tên là .venv
python -m venv .venv

# Kích hoạt môi trường (dành cho Windows PowerShell)
.\.venv\Scripts\activate

# (Dành cho macOS / Linux)
# source .venv/bin/activate
```
*Dấu hiệu nhận biết bạn đã kích hoạt thành công là có chữ `(.venv)` xuất hiện ở đầu dòng lệnh terminal.*

### Cài đặt thư viện phụ thuộc (Dependencies)
```bash
# Cập nhật pip lên phiên bản mới nhất
python -m pip install --upgrade pip

# Cài đặt các thư viện Data & CLI cơ bản
pip install pandas duckdb pyarrow tqdm rich typer

# Cài đặt các thư viện API (bổ sung nếu có file requirements.txt)
pip install fastapi uvicorn pydantic
```
*(Lưu ý: Nếu trong tương lai dự án có cung cấp file `requirements.txt` hoặc dùng `poetry`/`uv`, hãy cài đặt theo chuẩn công cụ đó).*

---

## 5. Tải Dataset từ HuggingFace
Dự án sử dụng tập dữ liệu **ViFinQA**. Chúng ta sẽ tải tập dữ liệu này trực tiếp vào đúng thư mục thiết kế `data/raw/` bằng lệnh `git clone`. 

*Ghi chú: Thư mục `data/` đã được ignore để không bị push nhầm các file khổng lồ lên GitHub.*

```bash
# Clone dataset vào đúng vị trí
git clone https://huggingface.co/datasets/AIGuruTinix/ViFinQA data/raw/ViFinQA
```

---

## 6. Thiết lập Môi trường Frontend (Next.js)
Giao diện người dùng Dashboard được xây dựng bằng Next.js 15.

```bash
# Chuyển vào thư mục frontend
cd frontend

# Cài đặt các gói phụ thuộc của Node.js
npm install


```

---

## 7. Chạy dự án (Run locally)
Để hệ thống hoạt động hoàn chỉnh, bạn cần chạy song song Backend và Frontend ở 2 cửa sổ terminal riêng biệt.

### Khởi động Backend API (FastAPI)
Mở một terminal, ở thư mục gốc `finagent` (nhớ phải kích hoạt `(.venv)` trước):

```bash
# Lệnh chạy server uvicorn (ví dụ với file src/app/main.py)
# Tuỳ thuộc vào điểm bắt đầu (entry point) cụ thể của API mà sửa lại đường dẫn module
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```
- Backend API sẽ chạy tại: **http://localhost:8000**
- API Documentation (Swagger UI) có sẵn tại: **http://localhost:8000/docs**

### Khởi động Frontend (Next.js)
Mở một cửa sổ terminal khác, di chuyển vào thư mục `frontend`:

```bash
cd frontend
npm run dev
```
- Giao diện Web sẽ khả dụng tại: **http://localhost:3000**

---

## 8. Workflow hàng ngày của Developer
1. Luôn cập nhật code mới nhất từ nhánh `dev`: 
   ```bash
   git checkout dev
   git pull origin dev
   ```
2. Checkout sang nhánh cá nhân của bạn để code: 
   ```bash
   git checkout nguyen 
   # hoặc git checkout minh
   ```
3. Sau khi code và test ổn định, đẩy (push) nhánh cá nhân của bạn lên GitHub và tạo Pull Request (PR) về nhánh `dev`.
4. Xem chi tiết các tính năng cần phát triển tại mục **Checklist phát triển** trong file [README.md](../README.md).

🎉 **Chúc bạn có những giờ làm việc năng suất và thú vị với NewGenAI Financial Agent!**
