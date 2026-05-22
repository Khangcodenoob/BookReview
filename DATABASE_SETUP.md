# BookReview PostgreSQL Setup

Tài liệu này hướng dẫn chuyển hệ thống BookReview từ SQLite sang PostgreSQL mà không phá vỡ code hiện tại.

## 1) Cài PostgreSQL

### Windows
- Tải PostgreSQL tại trang chính thức: [https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)
- Cài đặt `postgresql` + `psql` command-line tool.
- Ghi nhớ:
  - username (thường là `postgres`)
  - password
  - port (mặc định `5432`)

### Kiểm tra
```bash
psql --version
```

## 2) Tạo database và schema

File schema đã được tạo sẵn tại:
- `database_postgresql.sql`

### Cách chạy bằng psql
```bash
psql -U postgres -h localhost -p 5432 -f database_postgresql.sql
```

Lưu ý:
- Script có `CREATE DATABASE bookreview;`
- Sau khi tạo DB, cần kết nối vào DB `bookreview` để chạy phần còn lại (psql hỗ trợ `\c bookreview`).

Nếu client SQL của bạn không hỗ trợ `\c`, chia thành 2 bước:
1. Chạy riêng câu `CREATE DATABASE bookreview;`
2. Kết nối DB `bookreview`, sau đó chạy phần còn lại của file.

## 3) Cấu hình Flask dùng PostgreSQL

Dự án đang dùng `config.py` với biến môi trường `DATABASE_URL`.  
Bạn nên đặt biến môi trường như sau:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/bookreview
```

Hoặc (khuyến nghị) dùng driver psycopg:

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/bookreview
```

## 4) Đề xuất chỉnh `config.py`

Hiện tại `config.py` vẫn fallback về SQLite để không làm vỡ local dev.

Nếu muốn ưu tiên PostgreSQL theo yêu cầu triển khai, có thể chỉnh:

```python
SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/bookreview"
)
```

Khuyến nghị an toàn hơn (không phá vỡ code hiện tại):
- giữ fallback SQLite trong môi trường development
- chỉ set `DATABASE_URL` ở staging/production.

## 5) Migration (Flask-Migrate / Alembic)

Dự án có thư mục `migrations/` và file migration `0001_ecommerce_init.py`, nhưng hiện code đang chạy song song:
- SQLAlchemy models (`models.py`) cho phần e-commerce
- sqlite3 raw SQL (`app.py`) cho nhiều bảng khác (reviews, tags, bookmarks, social, challenges...)

Vì vậy:
- Script `database_postgresql.sql` là cách bootstrap đầy đủ nhất hiện tại.
- Migration Alembic hiện chưa bao phủ toàn bộ bảng raw SQL.

Nếu muốn migration chuẩn hóa:
1. Bổ sung model SQLAlchemy cho các bảng còn thiếu.
2. Tạo migration mới từ metadata thống nhất.
3. Chỉ giữ 1 nguồn sự thật schema (không trộn sqlite3 raw SQL + ORM).

## 6) Gói Python cần thiết

Đảm bảo có PostgreSQL driver:

```bash
pip install psycopg[binary]
```

Hoặc:

```bash
pip install psycopg2-binary
```

## 7) Kiểm tra kết nối

Sau khi set `DATABASE_URL`, chạy app và kiểm tra:
- đăng nhập
- danh sách sách
- review
- giỏ hàng / orders / payments
- bookmarks / shelves / follows / challenges

Nếu lỗi schema mismatch, đối chiếu lại với `database_postgresql.sql`.
