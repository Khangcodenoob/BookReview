# Changelog - Các cải thiện đã thực hiện

## [E-commerce Refactor] - 2026-03

### Refactor website Review Sách -> Buôn bán sách (E-commerce)

#### Database
- Schema e-commerce: users, categories, books (price, stock, isbn, is_active), orders, order_items (snapshot title/unit_price), payments.
- Cart: session-based (session["cart"]).
- Indexes: orders(user_id, created_at, status), order_items(order_id, book_id), categories(slug).

#### Customer
- Catalog: trang chủ, danh sách sách (pagination), filter theo category (dropdown từ DB), search title/author, sort (price asc/desc, newest).
- Book detail: thông tin, giá, tồn kho, nút "Thêm vào giỏ", reviews giữ nguyên.
- Cart: add/update/remove, subtotal, shipping (30k / free ship nếu subtotal > 300k), total.
- Checkout: đăng nhập bắt buộc, tạo order + order_items trong transaction, trừ stock an toàn (UPDATE ... WHERE stock >= q), clear cart, Payment COD/mock.
- My Orders / Order detail.

#### Admin
- Dashboard: Quản lý sách, Categories, Đơn hàng, Tài khoản, Duyệt review.
- CRUD books (create/edit/delete soft), upload cover, price, stock.
- CRUD categories (tự sinh slug từ tên).
- Quản lý orders: đổi status (pending/paid/shipped/canceled), đánh dấu đã thanh toán.

#### UI
- Navbar: Home, Sách, dropdown Danh mục (từ DB), Giỏ hàng (badge), Đơn hàng, Admin (nếu admin), Login/Logout.
- Templates: cart.html, orders.html, order_detail.html, admin/orders.html, admin/order_detail.html.

#### Bảo mật & chất lượng
- CSRF (Flask-WTF), validate input, password hashing (werkzeug), SECRET_KEY từ .env.
- Checkout: atomic stock decrement (không âm), rollback nếu hết hàng.

#### Tài khoản mặc định (sau khi chạy app lần đầu / ensure_schema)
- Admin: email `admin@example.com` hoặc username `admin`, mật khẩu `password`.
- Customer demo: email `customer@example.com`, username `customer_demo`, mật khẩu `password`.

---

## [Unreleased] - 2024

### Đã hoàn thành

#### Security Improvements
- **SECRET_KEY từ environment variables**: Không còn hardcode trong code
- **CSRF Protection**: Thêm Flask-WTF với CSRF protection
- **Rate Limiting**: Cải thiện rate limiting với Flask-Limiter
- **Configuration Management**: Class-based config với support cho dev/prod/test

#### Code Organization
- **Utils Modules**: Tách code thành modules có tổ chức
  - `utils/db.py` - Database helpers
  - `utils/auth.py` - Authentication decorators  
  - `utils/markdown.py` - Markdown processing
  - `utils/images.py` - Image handling
- **Config Module**: `config.py` với environment-based configuration
- **Migration Scripts**: `run_migrations.py` để chạy database migrations

#### Performance Improvements
- **Database Indexes**: Thêm indexes cho tất cả các bảng quan trọng
  - Books: title, author, genre, category_id, created_at
  - Reviews: book_id, status, reviewer, created_at
  - Bookmarks, User shelves, Follows, và nhiều hơn nữa
- **Caching Support**: Thêm Flask-Caching (cần integrate vào routes)

#### Code Cleanup
- **Remove Debug Code**: Xóa tất cả console.log và debug statements
- **Clean Templates**: Dọn dẹp debug code trong templates
- **Better Logging**: Thêm proper logging setup

#### Dependencies
- Thêm `Flask-WTF==1.2.1` cho CSRF protection
- Thêm `WTForms==3.1.1` cho form handling
- Thêm `Flask-Caching==2.1.0` cho caching
- Thêm `python-dotenv==1.0.0` cho environment variables

### Đang thực hiện

#### Code Refactoring
- Hoàn thiện việc thay thế helper functions trong app.py bằng utils imports
- Tách routes thành Blueprints (books, auth, reviews, admin, api)

#### Caching Integration
- Thêm caching cho book lists
- Thêm caching cho user data
- Thêm caching cho search results

### Cần làm tiếp

#### Error Handling
- [ ] Thêm proper error handlers (404, 500, etc.)
- [ ] Cải thiện error messages cho users
- [ ] Thêm error logging

#### API Improvements
- [ ] Mở rộng REST API endpoints
- [ ] Thêm API documentation
- [ ] Thêm API versioning

#### Testing
- [ ] Unit tests cho utils modules
- [ ] Integration tests cho routes
- [ ] Frontend tests

#### Documentation
- [ ] API documentation
- [ ] Code comments
- [ ] Developer guide

## Migration Guide

### Từ version cũ

1. **Backup database**:
   ```bash
   cp books.db books.db.backup
   ```

2. **Cài đặt dependencies mới**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Tạo .env file**:
   ```bash
   cp .env.example .env
   # Chỉnh sửa .env với SECRET_KEY của bạn
   ```

4. **Chạy migrations**:
   ```bash
   python run_migrations.py
   ```

5. **Test ứng dụng**:
   ```bash
   python app.py
   ```

### Breaking Changes

- **SECRET_KEY**: Bây giờ phải set trong `.env` file
- **Config**: Sử dụng class-based config thay vì dict
- **Utils**: Helper functions đã được move sang utils modules

### Deprecated

- Không có

## Notes

- Tất cả thay đổi đều backward compatible
- Database migrations có thể chạy nhiều lần (idempotent)
- Backup database trước khi chạy migrations
- Test kỹ trước khi deploy production
