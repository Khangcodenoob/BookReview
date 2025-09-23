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
G:\Kho 2\BookReview\
├─ app.py                      # Ứng dụng Flask chính: routes, auth, migrate động, CRUD admin, xử lý ảnh bìa
├─ schema.sql                  # Lược đồ DB khởi tạo (SQLite) khi tạo mới
├─ books.db                    # CSDL runtime (sao chép/backup để lưu dữ liệu)
├─ books.db.bak                # Bản sao lưu DB (tuỳ chọn)
├─ requirements.txt            # Danh sách thư viện Python cần cài
├─ update_covers.py            # Script cập nhật/tải ảnh bìa cho sách (batch)
├─ quick_update.py             # Script tiện ích cập nhật nhanh các trường/ dữ liệu nhỏ
├─ README.md                   # Tài liệu hướng dẫn dự án
│
├─ scripts\                    # Bộ script thao tác dữ liệu/ảnh bìa (batch/tools)
│  ├─ add_30_books.py          # Thêm nhanh ~30 sách mẫu để thử nghiệm
│  ├─ create_placeholder_covers.py # Tạo ảnh placeholder cho sách thiếu bìa
│  ├─ fix_covers_and_codes.py  # Sửa dữ liệu bìa và sinh/điều chỉnh book_code hàng loạt
│  ├─ google_books_covers.py   # Lấy ảnh bìa từ Google Books API theo tiêu đề/tác giả
│  ├─ list_covers.py           # Liệt kê, kiểm tra hiện trạng ảnh bìa trong DB/thư mục
│  ├─ maintain_books.py        # Tác vụ bảo trì dữ liệu sách (gộp/cập nhật định kỳ)
│  ├─ manual_book_covers.py    # Gán ảnh bìa thủ công từ danh sách URL/đường dẫn
│  ├─ run_and_report.py        # Chạy các tác vụ và xuất báo cáo ngắn gọn
│  ├─ seed_books.py            # Seed dữ liệu sách cơ bản
│  ├─ simple_cover_update.py   # Cập nhật cover_url đơn giản theo quy tắc đã định
│  ├─ update_book_covers.py    # Cập nhật bìa từ nhiều nguồn, ưu tiên ảnh thật
│  ├─ update_cover_urls.py     # Chuẩn hoá/sửa cover_url (HTTP→HTTPS, đường dẫn nội bộ…)
│  └─ update_real_book_covers.py # Thay placeholder bằng ảnh bìa thật nếu tìm thấy
│
├─ static\
│  ├─ styles.css               # Toàn bộ style: bố cục, màu sắc, navbar, footer, bảng, form
│  ├─ chat-widget.js           # Widget chat nổi (gợi ý sách nhanh, luôn hiển thị)
│  ├─ chat.js                  # Logic trang chat riêng `templates/chat.html`
│  ├─ animations.js            # Hiệu ứng nhỏ (transition/animation)
│  ├─ logo.svg                 # Logo trang
│  ├─ favicon.svg              # Biểu tượng trang (tab)
│  ├─ placeholder.jpg          # Ảnh dự phòng khi thiếu bìa
│  ├─ chat.js.bak              # Bản lưu tạm chat.js
│  ├─ avatars\                 # Ảnh đại diện người dùng (được upload)
│  │  ├─ 1.jpg
│  │  ├─ 2.jpg
│  │  └─ 3.jpg
│  └─ uploads\                 # Ảnh bìa tải về nội bộ (app tự tạo, cần quyền ghi)
│     └─ ... nhiều file ảnh
│
└─ templates\
   ├─ base.html                # Khung trang: header/nav danh mục, khu vực flash, footer, chat widget
   ├─ index.html               # Trang chủ: sách mới, top tuần, trending
   ├─ books_list.html          # Danh sách sách + tìm kiếm, lọc, sắp xếp, phân trang
   ├─ book_detail.html         # Chi tiết sách + review đã duyệt, votes, comments, tags
   ├─ login.html               # Đăng nhập
   ├─ register.html            # Đăng ký
   ├─ profile.html             # Trang cá nhân: avatar, bookmarks, review của tôi
   ├─ password_forgot.html     # Quên mật khẩu
   ├─ password_reset.html      # Đặt lại mật khẩu
   ├─ chat.html                # Trang chat gợi ý (sử dụng `static/chat.js`)
   ├─ chat.html.bak            # Bản lưu tạm của chat.html
   ├─ admin_books.html         # Quản trị sách: thống kê, danh sách, thao tác nhanh
   ├─ admin_book_form.html     # Thêm/Sửa sách: upload/URL bìa, danh mục, thể loại, tags
   ├─ admin_reviews.html       # Hàng chờ duyệt review
   ├─ admin_review_edit.html   # Sửa chi tiết review (details - markdown), trạng thái
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
