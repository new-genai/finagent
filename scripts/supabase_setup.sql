-- Kích hoạt extension pgvector
create extension if not exists vector;

-- Xóa bảng cũ nếu có để khởi tạo lại đúng cấu trúc nén halfvec
drop table if exists documents cascade;

-- Tạo bảng documents để lưu trữ Metadata và Vector Embedding của từng Table
create table documents (
    id bigserial primary key,
    table_id text not null,          -- ID của bảng, ví dụ: VNM_2023_page12_table1
    duckdb_table text,               -- Tên bảng gốc (có thể trùng table_id)
    company text,                    -- Mã công ty, ví dụ: VNM
    year text,                       -- Năm, ví dụ: 2023
    table_category text,             -- Phân loại bảng (Cân đối kế toán, KQKD...)
    report_type text,                -- Loại báo cáo (Hợp nhất, Riêng lẻ)
    headers text[],                  -- Tiêu đề các cột
    keywords text[],                 -- Các từ khóa/chỉ tiêu quan trọng trong bảng
    content text,                    -- Văn bản tóm tắt của bảng để dùng cho RAG/Embedding
    embedding halfvec(1024),         -- Vector embedding của BGE-m3 (Dimension: 1024, Half Precision)
    constraint table_id_unique unique (table_id)
);

-- Tạo Index HNSW để tăng tốc độ truy vấn vector
create index if not exists documents_embedding_idx on documents using hnsw (embedding halfvec_cosine_ops);

-- Xóa hàm cũ nếu có để tránh lỗi nạp chồng (overloading)
drop function if exists match_documents(vector(1024), float, int, text, text);
drop function if exists match_documents(halfvec(1024), float, int, text, text);

-- Tạo hàm RPC để cho phép gọi từ API Client (Python) để tìm kiếm vector
create or replace function match_documents (
  query_embedding halfvec(1024),
  match_threshold float,
  match_count int,
  p_company text default null,
  p_year text default null
) returns table (
  id bigint,
  table_id text,
  duckdb_table text,
  company text,
  year text,
  table_category text,
  report_type text,
  headers text[],
  keywords text[],
  content text,
  similarity float
)
language sql stable
as $$
  with filtered_docs as (
    select * from documents
    where (p_company is null or company = p_company)
      and (p_year is null or year = p_year)
  )
  select
    id,
    table_id,
    duckdb_table,
    company,
    year,
    table_category,
    report_type,
    headers,
    keywords,
    content,
    1 - (embedding <=> query_embedding) as similarity
  from filtered_docs
  where 1 - (embedding <=> query_embedding) > match_threshold
  order by embedding <=> query_embedding
  limit match_count;
$$;
