# Hướng dẫn Setup và Sử dụng các Cải thiện

## E-commerce: Lệnh chạy nhanh

```bash
# 1. Tạo venv (khuyến nghị)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# 2. Cài đặt dependencies
pip install -r requirements.txt

# 3. (Tùy chọn) Biến môi trường - tạo file .env ở thư mục gốc
# SECRET_KEY=your-secret-key
# FLASK_ENV=development

# 4. Chạy ứng dụng (tự tạo DB và schema nếu chưa có)
python app.py
```

Lần chạy đầu tiên sẽ:
- Tạo `books.db` nếu chưa có
- Chạy ensure_schema: tạo bảng categories, orders, order_items, payments, cột e-commerce trên books, seed admin và customer demo.

**Nếu đã có DB từ migration Alembic:**

```bash
# Trong thư mục gốc dự án
flask db upgrade
# hoặc
alembic upgrade head
```

**Chạy seed dữ liệu mẫu (categories + sách):**

```bash
python scripts/seed_ecommerce.py
```

**Chạy thêm index (SQL):**

```bash
python scripts/run_migrations.py
# hoặc
sqlite3 books.db < migrations/add_indexes.sql
```

### Tài khoản mặc định

| Vai trò   | Đăng nhập (email hoặc username) | Mật khẩu  |
|-----------|----------------------------------|-----------|
| Admin     | admin@example.com hoặc admin     | password  |
| Customer  | customer@example.com hoặc customer_demo | password  |

---

## Cài đặt chi tiết

### 1. Cài đặt dependencies mới

```bash
pip install -r requirements.txt
```

Các package mới được thêm:
- `Flask-WTF==1.2.1` - CSRF protection
- `WTForms==3.1.1` - Form handling
- `Flask-Caching==2.1.0` - Caching support
- `python-dotenv==1.0.0` - Environment variables

### 2. Tạo file .env

```bash
# Copy file mẫu
cp .env.example .env

# Hoặc tạo thủ công
```

Chỉnh sửa `.env` với các giá trị của bạn:

```env
# Bắt buộc cho production
SECRET_KEY=your-very-secret-key-here-change-this

# Optional - Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-password
FROM_EMAIL=noreply@hybibooks.vn

# Optional - reCAPTCHA
RECAPTCHA_SECRET=your-recaptcha-secret
RECAPTCHA_SITE_KEY=your-recaptcha-site-key

# Optional - Caching (Redis)
# CACHE_TYPE=redis
# CACHE_REDIS_URL=redis://localhost:6379/0
```

### 3. Chạy Database Migrations

Để thêm indexes cho performance:

```bash
python run_migrations.py
```

Hoặc chạy thủ công:

```bash
sqlite3 books.db < migrations/add_indexes.sql
```

## Sử dụng

### Chạy ứng dụng

```bash
python app.py
```

Ứng dụng sẽ tự động:
- Load config từ `.env`
- Tạo thư mục uploads nếu chưa có
- Khởi tạo database nếu chưa có

### Environment Variables

Ứng dụng sẽ tự động detect environment:
- `FLASK_ENV=development` - Development mode (default)
- `FLASK_ENV=production` - Production mode (yêu cầu SECRET_KEY)
- `FLASK_ENV=testing` - Testing mode

## Security Improvements

### CSRF Protection

CSRF protection đã được bật tự động. Tất cả forms cần có CSRF token:

```html
<form method="POST">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
  <!-- form fields -->
</form>
```

### Rate Limiting

Rate limiting đã được cấu hình:
- Default: 200 requests/day, 50 requests/hour
- Có thể customize trong `config.py`

### SECRET_KEY

**QUAN TRỌNG**: Đổi SECRET_KEY trong production!

```bash
# Generate a secure key
python -c "import secrets; print(secrets.token_hex(32))"
```

Thêm vào `.env`:
```env
SECRET_KEY=<generated-key>
```

## Performance Improvements

### Database Indexes

Indexes đã được thêm cho:
- Books: title, author, genre, category_id, created_at
- Reviews: book_id, status, reviewer, created_at
- Bookmarks: user_id, book_id
- User shelves: user_id, shelf_type
- Và nhiều indexes khác

### Caching

Caching được bật tự động. Có thể cấu hình:

```env
# Simple cache (default)
CACHE_TYPE=simple

# Redis cache (production)
CACHE_TYPE=redis
CACHE_REDIS_URL=redis://localhost:6379/0
```

## Development

### Cấu trúc mới

```
app/
├── config.py          # Configuration
├── utils/             # Utility modules
│   ├── db.py         # Database helpers
│   ├── auth.py       # Auth decorators
│   ├── markdown.py   # Markdown processing
│   └── images.py     # Image handling
└── migrations/       # Database migrations
    └── add_indexes.sql
```

### Sử dụng Utils

```python
from utils.db import get_db
from utils.auth import login_required, admin_required
from utils.markdown import render_markdown_safe
from utils.images import download_cover_if_external
```

## Breaking Changes

### 1. SECRET_KEY

Nếu bạn đang chạy production, cần set SECRET_KEY trong `.env`:
- Session sẽ bị invalid nếu đổi SECRET_KEY
- Users sẽ cần login lại

### 2. Config Structure

Config giờ sử dụng class-based:
- `DevelopmentConfig` - Development
- `ProductionConfig` - Production (yêu cầu SECRET_KEY)
- `TestingConfig` - Testing

## Troubleshooting

### Lỗi: "SECRET_KEY must be set in production"

Thêm vào `.env`:
```env
SECRET_KEY=your-secret-key
```

### Lỗi: "Module not found: utils"

Đảm bảo bạn đang chạy từ thư mục gốc của project.

### Lỗi: CSRF token missing

Thêm CSRF token vào forms:
```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
```

## Notes

- Tất cả thay đổi đều backward compatible
- Database migrations có thể chạy nhiều lần (idempotent)
- Backup database trước khi chạy migrations
- Test kỹ trước khi deploy production

## Migration từ code cũ

Nếu bạn đang chạy code cũ:

1. Backup database:
   ```bash
   cp books.db books.db.backup
   ```

2. Cài đặt dependencies mới:
   ```bash
   pip install -r requirements.txt
   ```

3. Tạo `.env` file với SECRET_KEY

4. Chạy migrations:
   ```bash
   python run_migrations.py
   ```

5. Test ứng dụng:
   ```bash
   python app.py
   ```
