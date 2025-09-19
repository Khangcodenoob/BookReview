# Hybi Books – Website review đánh giá sách (Flask)

Dự án này là ứng dụng web quản lý và đọc review sách bằng Flask + SQLite. Frontend dùng Jinja templates + CSS/JS thuần, tập trung triển khai nhanh, dễ bảo trì và mở rộng.

## Tính năng chính
- Trang chủ: Carousel sách mới; Top tuần (review 7 ngày); Đang thịnh hành (kết hợp bookmark 30 ngày, review, độ mới, đa dạng thể loại).
- Danh sách sách: tìm kiếm, lọc theo danh mục/thể loại/NXB/số trang/ngày; sắp xếp; phân trang.
- Chi tiết sách: mô tả, điểm trung bình, review đã duyệt, bình luận theo luồng, vote hữu ích, báo cáo, bookmark.
- Người dùng: đăng ký/đăng nhập/đăng xuất; hồ sơ; upload/xóa avatar; xem bookmarks/reviews của mình.
- Admin: CRUD sách, danh mục, tags, users; duyệt review; công cụ sinh mã sách; sinh review mẫu dài; viết dài mô tả; sinh tóm tắt dài hàng loạt.
- Chat gợi ý: widget nổi đề xuất sách theo truy vấn hoặc theo cuốn hiện tại.

## Kiến trúc tổng quát
- Backend: `app.py` (routes, DB, render, auth nhẹ, migrate động, tải ảnh bìa ngoài về `static/uploads/`).
- DB: SQLite `books.db`; lược đồ khởi tạo `schema.sql`; migrate động thêm cột nếu thiếu.
- Frontend: templates trong `templates/`, style tại `static/styles.css`, JS tại `static/*.js`.

## Cấu trúc thư mục
```
G:\Kho 2\VIewCode\
├─ app.py                      # Ứng dụng Flask chính (routes, DB, admin, review…)
├─ schema.sql                  # Lược đồ DB ban đầu (SQLite)
├─ books.db                    # CSDL runtime
├─ books.db.bak                # (tuỳ chọn) bản sao lưu DB
├─ requirements.txt            # Thư viện Python
├─ update_covers.py            # Script hỗ trợ cập nhật ảnh bìa (tuỳ chọn)
├─ quick_update.py             # Script tiện ích (tuỳ chọn)
├─ README.md                   # Hướng dẫn dự án
│
├─ scripts\                    # Công cụ thao tác dữ liệu/ảnh bìa
│  ├─ add_30_books.py
│  ├─ create_placeholder_covers.py
│  ├─ fix_covers_and_codes.py
│  ├─ google_books_covers.py
│  ├─ list_covers.py
│  ├─ maintain_books.py
│  ├─ manual_book_covers.py
│  ├─ run_and_report.py
│  ├─ seed_books.py
│  ├─ simple_cover_update.py
│  ├─ update_book_covers.py
│  ├─ update_cover_urls.py
│  └─ update_real_book_covers.py
│
├─ static\
│  ├─ styles.css               # Toàn bộ style (header/nav/footer, grid, hiệu ứng…)
│  ├─ chat-widget.js           # Widget chat gợi ý
│  ├─ animations.js            # Hiệu ứng phụ
│  ├─ logo.svg                 # Logo header
│  ├─ favicon.svg              # Favicon tab trình duyệt
│  ├─ placeholder.jpg          # Ảnh dự phòng
│  ├─ avatars\                 # Ảnh đại diện người dùng
│  │  ├─ 1.jpg
│  │  ├─ 2.jpg
│  │  └─ 3.jpg
│  └─ uploads\                 # Ảnh bìa được tải về nội bộ (tự sinh khi chạy)
│     └─ ... nhiều file ảnh
│
└─ templates\
   ├─ base.html                # Khung trang, header + navbar danh mục + footer + chat
   ├─ index.html               # Trang chủ (carousel, top tuần, trending)
   ├─ books_list.html          # Danh sách + lọc/sort/phân trang
   ├─ book_detail.html         # Chi tiết sách + review, votes, comments, details
   ├─ login.html               # Đăng nhập
   ├─ register.html            # Đăng ký
   ├─ profile.html             # Trang cá nhân (bookmarks, reviews của tôi)
   ├─ password_forgot.html     # Quên mật khẩu
   ├─ password_reset.html      # Đặt lại mật khẩu
   ├─ chat.html                # Trang chat gợi ý (tuỳ chọn)
   ├─ admin_books.html         # Quản trị sách (danh sách + hành động nhanh)
   ├─ admin_book_form.html     # Thêm/Sửa sách (viết mô tả dài, tạo review biên tập)
   ├─ admin_reviews.html       # Hàng chờ duyệt review + liên kết nhanh
   ├─ admin_review_edit.html   # Sửa chi tiết review (details – markdown)
   ├─ admin_categories.html    # Quản trị danh mục
   ├─ admin_tags.html          # Quản trị tags
   └─ admin_users.html         # Quản trị người dùng
```

## Yêu cầu hệ thống
- Python 3.9+
- pip, venv (khuyến nghị)
- SQLite3

## Cách chạy nhanh
```
python -m venv .venv
# Windows PowerShell
. .venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python app.py
# Mở http://127.0.0.1:5000/
```
Khi DB mới/ trống, app seed vài sách mẫu và tạo admin mặc định: `admin` / `admin123`.

## Biến môi trường tùy chọn
- SMTP gửi email: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `FROM_EMAIL`
- reCAPTCHA: `RECAPTCHA_SECRET`

Ví dụ (PowerShell):
```
$env:SMTP_HOST="smtp.example.com"
$env:FROM_EMAIL="noreply@example.com"
python app.py
```

## Cơ sở dữ liệu (SQLite)
Bảng chính (rút gọn):
- `books(id, title, author, cover_url, description, genre, publisher, num_pages, book_code UNIQUE, category_id, created_at)`
- `reviews(id, book_id, reviewer, rating, content, details, status, moderated_at, moderated_by, reject_reason, created_at)`
- `users(id, username UNIQUE, password_hash, role, email UNIQUE?, created_at)`
- `bookmarks(user_id, book_id, created_at)` (PK kép)
- `categories`, `tags`, `book_tags(book_id, tag_id)`
- `review_votes`, `review_comments`, `review_reports`, `audit_log`

Migrate động: `app.py` tự thử `ALTER TABLE` để thêm các cột thiếu (vd: `genre`, `publisher`, `num_pages`, `book_code`, `status`, `details`, …). Nếu DB mới, `schema.sql` sẽ khởi tạo nhanh.

## Tài khoản & bảo mật
- Vai trò: `user`, `admin`.
- Mật khẩu băm `werkzeug.security`.
- Option rate-limit đăng nhập (nếu cài `flask-limiter`).
- reCAPTCHA khi đăng ký (nếu có `RECAPTCHA_SECRET`).

## Quản trị & quy trình
- `/admin/books`:
  - CRUD sách; gắn danh mục, thể loại, tags.
  - Công cụ: tự sinh mã sách; sinh review mẫu dài hàng loạt; sinh tóm tắt dài hàng loạt.
  - Trong sửa 1 sách: “Viết mô tả dài hơn” (mở rộng mô tả), “Tạo review biên tập” (review dài chất lượng).
- `/admin/reviews`:
  - Hàng chờ duyệt/từ chối; “Sửa chi tiết” để thêm `details` (markdown).
- `/admin/categories`, `/admin/tags`, `/admin/users` quản lý dữ liệu liên quan.

## Endpoints tiêu biểu
- Trang chủ `/`, danh sách `/books`, chi tiết `/books/<id>`
- Review: GET `/books/<id>/reviews/new`, POST `/books/<id>/reviews`
- Vote review `/reviews/<rid>/vote`; Bình luận `/reviews/<rid>/comments`; Báo cáo `/reviews/<rid>/report`
- Bookmark: POST `/books/<id>/bookmark`
- Hồ sơ `/me`; Auth: `/register`, `/login`, `/logout`, `/password/forgot`, `/password/reset/<token>`
- Admin Sách: `/admin/books`, `/admin/books/new`, `/admin/books/<id>/edit`, `/admin/books/<id>/delete`
- Admin tools: `/admin/books/fix-book-codes`, `/admin/reviews`, `/admin/reviews/generate-long`, `/admin/books/generate-summaries`, `/admin/books/<id>/enhance-description`, `/admin/books/<id>/generate-review`

## Tùy chỉnh giao diện (CSS/JS)
- `static/styles.css` quản lý toàn bộ style, biến màu, hiệu ứng.
  - Nút header dùng gradient xanh lá → xanh ngọc (có thể đổi ở `.site-header nav > a`).
  - Màu icon tách khỏi màu chữ: `--icon-primary`, `--icon-secondary`.
- Chat widget: `static/chat-widget.js`; hiệu ứng bổ trợ: `static/animations.js`.

## Triển khai
Chạy bằng gunicorn:
```
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```
Nhớ cấp quyền ghi `static/uploads/` (ảnh bìa tải về) và `static/avatars/` (avatar).

## Sao lưu/khôi phục
- Sao lưu: copy `books.db` (+ `static/uploads/`, `static/avatars/`).
- Khôi phục: dừng app → thay `books.db` → chạy lại.

## FAQ
- Ảnh bìa ngoài không hiện: kiểm tra quyền ghi `static/uploads/`.
- Thiếu cột DB: khởi động lại app (migrate động).
- Không gửi email: cần cấu hình biến `SMTP_*`.
- Đổi logo/favicon: thay `static/logo.svg`, `static/favicon.svg`.

---
Chúc bạn sử dụng vui vẻ và dễ mở rộng dự án!
