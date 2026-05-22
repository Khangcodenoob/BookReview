# Bao cao khao sat du an va ke hoach E-commerce

## 1) Khao sat du an hien tai

### Cau truc
- **App**: Application factory (`create_app()` trong `app.py`), khong tach blueprint.
- **Models**: `models.py` – User, Category, Book, Order, OrderItem, Payment (SQLAlchemy).
- **DB**: SQLite, `books.db`, connection trong `config.py` (`SQLALCHEMY_DATABASE_URI`, `DATABASE` cho raw SQL).
- **Auth**: Dang nhap/dang ky bang username hoac email, session `user_id`, `username`, `role`. Role: `user` | `admin`. Decorator `@login_required`, `@admin_required`.
- **Templates**: `base.html` (navbar, footer), `index.html`, `books_list.html`, `book_detail.html`, `cart.html`, `checkout` (POST tu cart), `orders.html`, `order_detail.html`, `admin/orders.html`, `admin/order_detail.html`, `admin_books.html`, `admin_book_form.html`, `admin_categories.html`.
- **Review**: Bang `reviews` (raw SQL), khong co model Review. Cac bang: reviews, review_votes, review_comments, review_reports.

### Nhung gi giu lai
- Auth (dang nhap, dang ky, session, password hashing, role user/admin).
- Layout, base template, CSS (styles.css, enhanced-styles.css, header-elegant.css).
- Templates book list, book detail, review form, profile, shelves, feed, challenges.
- Gio hang session-based, checkout tao Order/OrderItem/Payment, tru stock, clear cart.
- Trang My Orders, Order detail.
- Admin: CRUD books, categories, orders (doi status, danh dau thanh toan), users, reviews moderation.
- CSRF (Flask-WTF), config .env, SHIPPING_FEE / FREE_SHIP_THRESHOLD.

### Nhung gi can chinh/bo sung
- Navbar: thay the genre links co dinh bang **Categories dropdown** lay tu DB.
- Chuan hoa slug khi tao category (admin): tu dong sinh slug tu name.
- Checkout: dam bao tru stock an toan (chi UPDATE khi stock >= quantity, rollback neu het hang).
- Bao cao deliverables: danh sach file thay doi, lenh chay, tai khoan admin/customer mac dinh (da co trong ensure_schema: admin@example.com / password, customer@example.com / password).
- Index cho orders, order_items (da co trong migration/ add_indexes; bo sung neu thieu).

---

## 2) So do Database E-commerce (da co san)

- **users**: id, username, email, password_hash, role (user|admin), created_at
- **categories**: id, name unique, slug unique
- **books**: id, title, author, description, price, stock, isbn nullable unique, cover_url, category_id, genre (legacy), created_at, is_active
- **orders**: id, user_id, status (pending|paid|shipped|canceled), subtotal, shipping_fee, discount, total, created_at
- **order_items**: id, order_id, book_id, title_snapshot, unit_price, quantity, line_total
- **payments**: id, order_id, provider (cod|mock|...), amount, status, paid_at, txn_ref

Gio hang: **session-based** (session["cart"] = {book_id: quantity}). Ly do: don gian, khong can dang nhap de them gio, phu hop quy mo nho.

---

## 3) Ke hoach thuc thi theo step

| Step | Noi dung | Trang thai |
|------|----------|------------|
| 1 | Refactor models + migrations (schema e-commerce da co; bo sung index, slug category) | Done |
| 2 | Catalog + book detail (home, filter category, search, sort, book detail + Add to Cart) | Done |
| 3 | Cart (session, add/update/remove, shipping rule) | Done |
| 4 | Checkout + orders + payment (transaction, tru stock, clear cart) | Done |
| 5 | Admin CRUD (books, categories, orders) | Done |
| 6 | Deliverables: CHANGELOG, lenh chay, seed, tai khoan mac dinh | Done |

---

## 4) Danh sach file thay doi (tom tat)

| File | Ly do |
|------|--------|
| `app.py` | inject categories vao context; filter books theo category_id; admin category tu sinh slug; checkout kiem tra stock atomic (UPDATE WHERE stock >= q) |
| `templates/base.html` | Navbar: dropdown Danh mục từ DB (categories), JS toggleCategoriesDropdown, đóng dropdown khi click ngoài |
| `migrations/add_indexes.sql` | Index cho orders, order_items, categories.slug |
| `docs/SURVEY_AND_PLAN.md` | Bao cao khao sat va ke hoach (file nay) |
| `docs/CHANGELOG.md` | Ghi nhan refactor e-commerce |
| `docs/SETUP_GUIDE.md` | Them lenh chay nhanh: venv, pip install, python app.py, seed, tai khoan mac dinh |

Cac file da co san va giu nguyen: models.py, config.py, extensions.py, templates (cart, orders, order_detail, admin/orders, admin/order_detail, book_detail, books_list), scripts/seed_ecommerce.py, ensure_schema trong app.py (tao DB, seed admin/customer).
