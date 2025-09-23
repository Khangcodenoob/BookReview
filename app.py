import os
import time
import glob
import sqlite3
from functools import wraps
from typing import Callable, Any, List, Optional
from flask import Flask, render_template, g, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from markdown_it import MarkdownIt
import bleach


BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "books.db")

ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + ["p","pre","code","img","h1","h2","h3","h4","h5","h6","ul","ol","li","blockquote","hr","br","strong","em"]
ALLOWED_ATTRS = {"a":["href","title","rel","target"],"img":["src","alt","title","width","height"],"code":["class"]}
md = MarkdownIt("commonmark").enable("table").enable("strikethrough").enable("linkify")


def render_markdown_safe(text: str) -> str:
    html = md.render(text or "")
    # sanitize
    return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, protocols=["http","https","mailto"], strip=True)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret"
    app.config["DATABASE"] = DB_PATH
    # optional config via env
    app.config['SMTP_HOST'] = os.environ.get('SMTP_HOST')
    app.config['SMTP_PORT'] = int(os.environ.get('SMTP_PORT') or 25)
    app.config['SMTP_USER'] = os.environ.get('SMTP_USER')
    app.config['SMTP_PASS'] = os.environ.get('SMTP_PASS')
    app.config['FROM_EMAIL'] = os.environ.get('FROM_EMAIL')
    app.config['RECAPTCHA_SECRET'] = os.environ.get('RECAPTCHA_SECRET')

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])  # type: ignore[attr-defined]
            g.db.row_factory = sqlite3.Row  # type: ignore[attr-defined]
        return g.db  # type: ignore[attr-defined]

    # --- security helpers: tokens / email ---
    from itsdangerous import URLSafeTimedSerializer
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    def make_token(payload: str) -> str:
        return s.dumps(payload, salt='email-confirm')

    def parse_token(token: str, max_age: int = 3600*24) -> Optional[str]:
        try:
            return s.loads(token, salt='email-confirm', max_age=max_age)
        except Exception:
            return None

    def send_mail(subject: str, to_email: str, body: str) -> bool:
        # simple SMTP send — only used if SMTP config provided
        try:
            import smtplib
            from email.message import EmailMessage
            host = app.config.get('SMTP_HOST')
            if not host:
                return False
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = app.config.get('FROM_EMAIL') or 'noreply@example.com'
            msg['To'] = to_email
            msg.set_content(body)
            with smtplib.SMTP(host, app.config.get('SMTP_PORT', 25)) as smtp:
                if app.config.get('SMTP_USER'):
                    smtp.login(app.config.get('SMTP_USER'), app.config.get('SMTP_PASS'))
                smtp.send_message(msg)
            return True
        except Exception:
            return False

    # reCAPTCHA verification helper (server-side)
    def verify_recaptcha(response_token: str) -> bool:
        secret = app.config.get('RECAPTCHA_SECRET')
        if not secret or not response_token:
            return False
        try:
            import requests
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data={'secret': secret, 'response': response_token}, timeout=5)
            data = r.json()
            return data.get('success', False)
        except Exception:
            return False

    # rate limiter
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        limiter = Limiter(key_func=get_remote_address)
        limiter.init_app(app)
    except Exception:
        limiter = None

    # ---- Avatar helpers ----
    AVATAR_DIR = os.path.join(BASE_DIR, 'static', 'avatars')
    ALLOWED_AVATAR_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
    UPLOADS_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
    ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "gif", "webp", "webp"}

    def _ensure_avatar_dir():
        try:
            os.makedirs(AVATAR_DIR, exist_ok=True)
        except Exception:
            pass

    def _ensure_uploads_dir():
        try:
            os.makedirs(UPLOADS_DIR, exist_ok=True)
        except Exception:
            pass

    def _download_cover_if_external(url: str) -> str:
        """If url starts with http/https, try to download into static/uploads and return local path (/static/uploads/xxx).
        On failure or if url already local, return original url."""
        if not url:
            return url
        u = url.strip()
        if not (u.startswith('http://') or u.startswith('https://')):
            return u
        _ensure_uploads_dir()
        try:
            import requests
            from urllib.parse import urlparse
            resp = requests.get(u, timeout=8)
            if resp.status_code != 200 or not resp.content:
                return u
            parsed = urlparse(u)
            # derive filename
            name = os.path.basename(parsed.path) or f"cover_{int(time.time())}.jpg"
            safe = secure_filename(name)
            # ensure extension
            ext = safe.rsplit('.', 1)[-1].lower() if '.' in safe else 'jpg'
            if ext not in ALLOWED_IMAGE_EXT:
                ext = 'jpg'
                safe = f"{safe}.{ext}" if '.' not in safe else safe
            dest_name = safe
            dest_path = os.path.join(UPLOADS_DIR, dest_name)
            # avoid overwrite by appending counter
            base, dot, ex = dest_name.rpartition('.')
            i = 1
            while os.path.exists(dest_path):
                dest_name = f"{base}_{i}.{ex}"
                dest_path = os.path.join(UPLOADS_DIR, dest_name)
                i += 1
            with open(dest_path, 'wb') as f:
                f.write(resp.content)
            return '/static/uploads/' + dest_name
        except Exception:
            return u

    def _find_avatar_filename(user_id: int) -> Optional[str]:
        # look for files like 42.png, 42.jpg etc
        pattern = os.path.join(AVATAR_DIR, f"{user_id}.*")
        matches = glob.glob(pattern)
        if not matches:
            return None
        # return the basename of the first match
        return os.path.basename(matches[0])

    def _remove_existing_avatars(user_id: int):
        pattern = os.path.join(AVATAR_DIR, f"{user_id}.*")
        for p in glob.glob(pattern):
            try:
                os.remove(p)
            except Exception:
                pass

    @app.teardown_appcontext
    def close_db(exception):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    # ensure uploads dir exists at startup
    _ensure_uploads_dir()

    def _parse_tags_csv(raw: str) -> List[str]:
        parts = [p.strip() for p in (raw or "").split(",")]
        return [p for p in parts if p]

    def _ensure_tags(db: sqlite3.Connection, tags: List[str]) -> List[int]:
        tag_ids: List[int] = []
        for name in tags:
            row = db.execute("SELECT id FROM tags WHERE name=?", (name,)).fetchone()
            if row:
                tag_ids.append(int(row["id"]))
            else:
                cur = db.execute("INSERT INTO tags (name, slug) VALUES (?,?)", (name, None))
                tag_ids.append(int(cur.lastrowid))
        return tag_ids

    def _set_book_tags(db: sqlite3.Connection, book_id: int, tags: List[str]) -> None:
        db.execute("DELETE FROM book_tags WHERE book_id=?", (book_id,))
        if not tags:
            return
        tag_ids = _ensure_tags(db, tags)
        db.executemany(
            "INSERT OR IGNORE INTO book_tags (book_id, tag_id) VALUES (?,?)",
            [(book_id, tid) for tid in tag_ids],
        )

    # ---------------- Auth helpers (hoisted) ----------------
    def login_required(view_func: Callable[..., Any]):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                flash("Vui lòng đăng nhập.")
                return redirect(url_for("login", next=request.path))
            return view_func(*args, **kwargs)
        return wrapped

    def admin_required(view_func: Callable[..., Any]):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                flash("Vui lòng đăng nhập.")
                return redirect(url_for("login", next=request.path))
            if session.get("role") != "admin":
                flash("Bạn không có quyền truy cập.")
                return redirect(url_for("home"))
            return view_func(*args, **kwargs)
        return wrapped

    @app.route("/")
    def home():
        db = get_db()
        # fetch newest
        rows = db.execute(
            "SELECT id, title, author, cover_url, COALESCE(genre,'Khác') as genre, description, book_code, created_at FROM books ORDER BY created_at DESC LIMIT 12"
        ).fetchall()

        # If fewer than 8, fill the remainder with random distinct books
        if len(rows) < 8:
            if rows:
                ids = tuple(r["id"] for r in rows)
                placeholders = ",".join(["?"] * len(ids))
                extra = db.execute(
                    f"SELECT id, title, author, cover_url, COALESCE(genre,'Khác') as genre, description, book_code FROM books WHERE id NOT IN ({placeholders}) ORDER BY RANDOM() LIMIT ?",
                    (*ids, 8 - len(rows)),
                ).fetchall()
            else:
                extra = db.execute(
                    "SELECT id, title, author, cover_url, COALESCE(genre,'Khác') as genre, description, book_code FROM books ORDER BY RANDOM() LIMIT 8"
                ).fetchall()
            rows = list(rows) + list(extra)

        # Normalize covers (download external to local once) and ensure description fallbacks
        latest_books: List[dict] = []
        for r in rows:
            cover = _download_cover_if_external(r["cover_url"]) if r["cover_url"] else None
            latest_books.append({
                "id": r["id"],
                "title": r["title"],
                "author": r["author"],
                "cover_url": cover,
                "genre": r["genre"],
                "description": r["description"] or "",
                "book_code": r["book_code"],
            })

        # Guarantee at least 2 slides by duplicating the first when only one item
        if len(latest_books) == 1:
            latest_books.append(latest_books[0])

        # Topic sections
        # Top tuần: theo số review approved trong 7 ngày qua
        top_week = db.execute(
            """
            SELECT b.id, b.title, b.author, b.cover_url, COALESCE(b.genre,'Khác') as genre, b.description, b.book_code,
                   COUNT(r.id) as reviews_count
            FROM books b
            JOIN reviews r ON r.book_id=b.id AND r.status='approved' AND datetime(r.created_at) >= datetime('now','-7 day')
            GROUP BY b.id
            ORDER BY reviews_count DESC, b.created_at DESC
            LIMIT 8
            """
        ).fetchall()

        # Thịnh hành: Kết hợp nhiều tiêu chí để tạo sự đa dạng
        trending = db.execute(
            """
            WITH book_metrics AS (
                SELECT b.id, b.title, b.author, b.cover_url, COALESCE(b.genre,'Khác') as genre, b.description, b.book_code,
                       -- Điểm bookmark (30 ngày gần đây)
                       COALESCE(bookmark_score, 0) as bookmark_score,
                       -- Điểm review (tất cả thời gian)
                       COALESCE(review_score, 0) as review_score,
                       -- Điểm mới (sách mới có ưu tiên)
                       CASE WHEN datetime(b.created_at) >= datetime('now','-7 day') THEN 10
                            WHEN datetime(b.created_at) >= datetime('now','-30 day') THEN 5
                            ELSE 0 END as newness_score,
                       -- Điểm đa dạng thể loại (random để tránh tập trung 1 thể loại)
                       (ABS(RANDOM()) % 100) as diversity_score
                FROM books b
                LEFT JOIN (
                    SELECT book_id, COUNT(*) * 2 as bookmark_score
                    FROM bookmarks 
                    WHERE datetime(created_at) >= datetime('now','-30 day')
                    GROUP BY book_id
                ) bm ON b.id = bm.book_id
                LEFT JOIN (
                    SELECT book_id, COUNT(*) * 1.5 as review_score
                    FROM reviews 
                    WHERE status = 'approved'
                    GROUP BY book_id
                ) rv ON b.id = rv.book_id
            )
            SELECT id, title, author, cover_url, genre, description, book_code,
                   (bookmark_score + review_score + newness_score + diversity_score) as total_score
            FROM book_metrics
            ORDER BY total_score DESC, RANDOM()
            LIMIT 8
            """
        ).fetchall()

        genres = db.execute("SELECT DISTINCT COALESCE(genre,'Khác') AS g FROM books ORDER BY g").fetchall()
        return render_template(
            "index.html",
            latest_books=latest_books,
            genres=[row[0] for row in genres],
            top_week=top_week,
            trending=trending,
        )

    @app.route("/books")
    def books_list():
        db = get_db()
        # query params
        q = (request.args.get("q") or "").strip()
        selected_genre = (request.args.get("genre") or "").strip()
        publisher = (request.args.get("publisher") or "").strip()
        pages_min = (request.args.get("pages_min") or "").strip()
        pages_max = (request.args.get("pages_max") or "").strip()
        date_from = (request.args.get("date_from") or "").strip()
        date_to = (request.args.get("date_to") or "").strip()
        sort = request.args.get("sort") or "new"
        try:
            page = max(1, int(request.args.get("page", 1)))
        except ValueError:
            page = 1
        try:
            per_page = max(6, min(24, int(request.args.get("per_page", 9))))
        except ValueError:
            per_page = 9

        where = []
        params = []
        if q:
            where.append("(title LIKE ? OR author LIKE ? OR book_code LIKE ?)")
            like = f"%{q}%"
            params += [like, like, like]
        if selected_genre:
            # match by category name first, fallback genre field
            where.append("(category_id IN (SELECT id FROM categories WHERE name = ?) OR genre = ?)")
            params += [selected_genre, selected_genre]
        if publisher:
            where.append("(publisher LIKE ?)")
            params.append(f"%{publisher}%")
        if pages_min:
            try:
                where.append("(num_pages >= ?)")
                params.append(int(pages_min))
            except ValueError:
                pass
        if pages_max:
            try:
                where.append("(num_pages <= ?)")
                params.append(int(pages_max))
            except ValueError:
                pass
        if date_from:
            where.append("(date(created_at) >= date(?))")
            params.append(date_from)
        if date_to:
            where.append("(date(created_at) <= date(?))")
            params.append(date_to)
        where_sql = (" WHERE " + " AND ".join(where)) if where else ""

        if sort == "az":
            order_sql = " ORDER BY title COLLATE NOCASE ASC"
        elif sort == "za":
            order_sql = " ORDER BY title COLLATE NOCASE DESC"
        else:
            order_sql = " ORDER BY created_at DESC"

        # count total
        total = db.execute(f"SELECT COUNT(1) AS c FROM books{where_sql}", params).fetchone()["c"]
        offset = (page - 1) * per_page
        books = db.execute(
            f"SELECT id, title, author, cover_url, description, COALESCE((SELECT name FROM categories c WHERE c.id = books.category_id), COALESCE(genre,'Khác')) as genre FROM books{where_sql}{order_sql} LIMIT ? OFFSET ?",
            params + [per_page, offset],
        ).fetchall()
        cat_rows = db.execute("SELECT name FROM categories ORDER BY name").fetchall()
        # fallback to genres if categories empty
        if cat_rows:
            genres = [r[0] for r in cat_rows]
        else:
            genres = [r["g"] for r in db.execute("SELECT DISTINCT COALESCE(genre,'Khác') AS g FROM books ORDER BY g").fetchall()]
        total_pages = (total + per_page - 1) // per_page
        return render_template(
            "books_list.html",
            books=books,
            q=q,
            selected_genre=selected_genre,
            publisher=publisher,
            pages_min=pages_min,
            pages_max=pages_max,
            date_from=date_from,
            date_to=date_to,
            sort=sort,
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            genres=genres,
        )

    @app.route("/books/<int:book_id>")
    def book_detail(book_id: int):
        db = get_db()
        book = db.execute(
            "SELECT id, title, author, cover_url, description, COALESCE(genre,'Khác') as genre, publisher, num_pages, book_code, category_id FROM books WHERE id=?",
            (book_id,),
        ).fetchone()
        if not book:
            flash("Không tìm thấy sách.")
            return redirect(url_for("books_list"))
        reviews = db.execute(
            "SELECT id, reviewer, rating, content, details, created_at, status FROM reviews WHERE book_id=? AND status='approved' ORDER BY created_at DESC",
            (book_id,),
        ).fetchall()
        # votes count per review
        review_ids = [r["id"] for r in reviews]
        votes_map = {}
        if review_ids:
            qmarks = ",".join(["?"] * len(review_ids))
            rows = db.execute(f"SELECT review_id, COUNT(1) as c FROM review_votes WHERE review_id IN ({qmarks}) GROUP BY review_id", review_ids).fetchall()
            votes_map = {row["review_id"]: row["c"] for row in rows}
        # comments per review (threaded: parent_id)
        comments_map = {}
        if review_ids:
            qmarks = ",".join(["?"] * len(review_ids))
            rows = db.execute(f"SELECT id, review_id, parent_id, author, content, created_at FROM review_comments WHERE review_id IN ({qmarks}) ORDER BY created_at ASC", review_ids).fetchall()
            for row in rows:
                comments_map.setdefault(row["review_id"], []).append(row)
        tags = db.execute(
            "SELECT t.name FROM tags t JOIN book_tags bt ON bt.tag_id=t.id WHERE bt.book_id=? ORDER BY t.name",
            (book_id,),
        ).fetchall()
        avg_row = db.execute("SELECT ROUND(AVG(rating),1) as avg_rating, COUNT(1) as total FROM reviews WHERE book_id=? AND status='approved'", (book_id,)).fetchone()
        avg_rating = avg_row["avg_rating"] if avg_row and avg_row["avg_rating"] is not None else None
        total_reviews = avg_row["total"] if avg_row else 0
        # bookmark state
        is_bookmarked = False
        if session.get("user_id"):
            row = db.execute("SELECT 1 FROM bookmarks WHERE user_id=? AND book_id=?", (session["user_id"], book_id)).fetchone()
            is_bookmarked = bool(row)
        return render_template("book_detail.html", book=book, reviews=reviews, avg_rating=avg_rating, total_reviews=total_reviews, tags=[r[0] for r in tags], votes_map=votes_map, comments_map=comments_map, render_markdown=render_markdown_safe, is_bookmarked=is_bookmarked)

    @app.route("/books/<int:book_id>/reviews/new")
    def new_review(book_id: int):
        db = get_db()
        book = db.execute("SELECT id, title, author, cover_url, genre, publisher, description FROM books WHERE id=?", (book_id,)).fetchone()
        if not book:
            flash("Không tìm thấy sách.")
            return redirect(url_for("books_list"))
        return render_template("review_form.html", book=book)

    @app.route("/books/<int:book_id>/reviews", methods=["POST"])
    def create_review(book_id: int):
        reviewer = request.form.get("reviewer", "").strip()
        rating = request.form.get("rating", "").strip()
        content = request.form.get("content", "").strip()
        if not reviewer or not rating:
            flash("Vui lòng nhập tên và điểm đánh giá.")
            return redirect(url_for("new_review", book_id=book_id))
        try:
            rating_int = int(rating)
            if rating_int < 1 or rating_int > 5:
                raise ValueError
        except ValueError:
            flash("Điểm đánh giá phải từ 1 đến 5.")
            return redirect(url_for("new_review", book_id=book_id))

        db = get_db()
        # đảm bảo sách tồn tại
        book = db.execute("SELECT id FROM books WHERE id=?", (book_id,)).fetchone()
        if not book:
            flash("Không tìm thấy sách.")
            return redirect(url_for("books_list"))

        # reviews default to pending
        db.execute(
            "INSERT INTO reviews (book_id, reviewer, rating, content, status) VALUES (?,?,?,?,?)",
            (book_id, reviewer, rating_int, content, "pending"),
        )
        db.commit()
        flash("✅ Đã gửi đánh giá thành công, chờ duyệt!")
        return redirect(url_for("book_detail", book_id=book_id))

    # ---------------- Auth helpers (defined above) ----------------

    @app.context_processor
    def inject_user():
        uid = session.get("user_id")
        avatar_file = None
        if uid:
            avatar_file = _find_avatar_filename(uid)
        avatar_url = (url_for('static', filename=f'avatars/{avatar_file}') if avatar_file else None)
        return {
            "current_user": {
                "id": uid,
                "username": session.get("username"),
                "role": session.get("role"),
                "avatar_url": avatar_url,
            }
        }

    # ---------------- Auth routes ----------------
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = (request.form.get("email", "") or request.form.get("username", "")).strip()
            username = (request.form.get("username", "") or email.split('@')[0]).strip()
            password = request.form.get("password", "").strip()
            recaptcha = request.form.get('g-recaptcha-response', '')
            # if reCAPTCHA configured, enforce
            if app.config.get('RECAPTCHA_SECRET') and not verify_recaptcha(recaptcha):
                flash('Xác thực reCAPTCHA thất bại.')
                return redirect(url_for('register'))
            if not email or not username or not password:
                flash("Vui lòng nhập email, tên đăng nhập và mật khẩu.")
                return redirect(url_for("register"))
            db = get_db()
            # ensure email column exists (runtime migration)
            try:
                cols = db.execute("PRAGMA table_info(users)").fetchall()
                names = {c[1] for c in cols}
                if 'email' not in names:
                    # SQLite does not support UNIQUE in ADD COLUMN
                    db.execute("ALTER TABLE users ADD COLUMN email TEXT")
                    db.commit()
                    # add unique index separately (safe if duplicates don't exist)
                    db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)")
                    db.commit()
            except Exception:
                pass
            exists = db.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone()
            if exists:
                flash("Tên đăng nhập đã tồn tại.")
                return redirect(url_for("register"))
            if email:
                try:
                    exists_mail = db.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone()
                except Exception:
                    exists_mail = None
                if exists_mail:
                    flash("Email đã được sử dụng.")
                    return redirect(url_for("register"))
            db.execute(
                "INSERT INTO users (username, password_hash, role, email) VALUES (?,?,?,?)",
                (username, generate_password_hash(password), "user", email),
            )
            db.commit()
            # send verification email if email provided in username@ form (optional)
            try:
                token = make_token(username)
                verify_url = url_for('verify_email', token=token, _external=True)
                send_mail('Xác thực tài khoản', username, f'Nhấn vào đây để xác thực: {verify_url}')
            except Exception:
                pass
            flash("Đăng ký thành công. Kiểm tra email để xác thực nếu có.")
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route('/verify/<token>')
    def verify_email(token: str):
        val = parse_token(token)
        if not val:
            flash('Token không hợp lệ hoặc đã hết hạn.')
            return redirect(url_for('home'))
        # here val is username (email) if used that way; mark user verified if you have such column
        flash('Tài khoản đã được xác thực (nếu tồn tại).')
        return redirect(url_for('login'))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            # optional rate limit on login attempts
            if limiter:
                try:
                    limiter.limit("10 per minute")(lambda: None)()
                except Exception:
                    pass
            db = get_db()
            # allow login by username or email
            user = db.execute("SELECT id, username, password_hash, role FROM users WHERE username=?", (username,)).fetchone()
            if not user:
                try:
                    user = db.execute("SELECT id, username, password_hash, role FROM users WHERE email=?", (username,)).fetchone()
                except Exception:
                    user = None
            if not user or not check_password_hash(user["password_hash"], password):
                flash("Sai thông tin đăng nhập.")
                return redirect(url_for("login"))
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            next_url = request.args.get("next") or url_for("home")
            return redirect(next_url)
        return render_template("login.html")

    @app.route('/password/forgot', methods=['GET','POST'])
    def password_forgot():
        if request.method == 'POST':
            email = (request.form.get('email') or '').strip()
            db = get_db()
            # try by email first, fallback username
            row = None
            try:
                row = db.execute('SELECT id, username FROM users WHERE email=?', (email,)).fetchone()
            except Exception:
                row = None
            if not row:
                row = db.execute('SELECT id, username FROM users WHERE username=?', (email,)).fetchone()
            if row:
                token = make_token(str(row['id']))
                reset_url = url_for('password_reset', token=token, _external=True)
                send_mail('Yêu cầu đặt lại mật khẩu', email, f'Nhấn vào đây để đặt lại mật khẩu: {reset_url}')
            flash('Nếu email tồn tại, một liên kết đặt lại mật khẩu đã được gửi.')
            return redirect(url_for('login'))
        return render_template('password_forgot.html')

    @app.route('/password/reset/<token>', methods=['GET','POST'])
    def password_reset(token: str):
        uid = parse_token(token)
        if not uid:
            flash('Token không hợp lệ hoặc đã hết hạn.')
            return redirect(url_for('login'))
        if request.method == 'POST':
            pw = (request.form.get('password') or '').strip()
            if not pw:
                flash('Vui lòng nhập mật khẩu mới.')
                return redirect(request.url)
            db = get_db()
            db.execute('UPDATE users SET password_hash=? WHERE id=?', (generate_password_hash(pw), int(uid)))
            db.commit()
            flash('Đã cập nhật mật khẩu. Hãy đăng nhập.')
            return redirect(url_for('login'))
        return render_template('password_reset.html')

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Đã đăng xuất.")
        return redirect(url_for("home"))

    @app.route('/chat')
    def chat():
        return render_template('chat.html')

    @app.route('/api/chat/suggest', methods=['POST'])
    def api_chat_suggest():
        data = request.get_json() or {}
        q = (data.get('q') or '').strip()
        seed = data.get('seed_book_id') or data.get('seed')
        db = get_db()
        suggestions = []
        # If a seed book id is provided, find similar books by genre/author/tags
        sid = None
        if seed:
            try:
                sid = int(seed)
            except Exception:
                sid = None
        if sid:
            # try same genre/author first
            row = db.execute('SELECT genre, author FROM books WHERE id=?', (sid,)).fetchone()
            if row:
                genre = row['genre']
                author = row['author']
                rows = db.execute(
                    'SELECT id, title, author, cover_url, description FROM books WHERE id!=? AND (genre=? OR author=?) LIMIT 8',
                    (sid, genre, author),
                ).fetchall()
                suggestions = list(rows)
            # then try shared tags
            tag_rows = db.execute('SELECT t.id FROM tags t JOIN book_tags bt ON bt.tag_id=t.id WHERE bt.book_id=?', (sid,)).fetchall()
            if tag_rows:
                tag_ids = [str(r['id']) for r in tag_rows]
                qmarks = ','.join(['?'] * len(tag_ids))
                rows2 = db.execute(
                    f"SELECT DISTINCT b.id, b.title, b.author, b.cover_url, b.description FROM books b JOIN book_tags bt ON bt.book_id=b.id WHERE bt.tag_id IN ({qmarks}) AND b.id!=? LIMIT 8",
                    tuple(tag_ids) + (sid,),
                ).fetchall()
                # merge without duplicates
                seen = {r['id'] for r in suggestions}
                for r in rows2:
                    if r['id'] not in seen:
                        suggestions.append(r)
                        seen.add(r['id'])
        elif q:
            like = f"%{q}%"
            suggestions = db.execute(
                'SELECT id, title, author, cover_url, description FROM books WHERE title LIKE ? OR author LIKE ? OR description LIKE ? LIMIT 8',
                (like, like, like),
            ).fetchall()
        else:
            suggestions = db.execute('SELECT id, title, author, cover_url, description FROM books ORDER BY created_at DESC LIMIT 6').fetchall()

        out = []
        for r in suggestions:
            short = (r['description'] or '')[:160]
            out.append({
                'id': r['id'],
                'title': r['title'],
                'author': r['author'],
                'cover_url': r['cover_url'],
                'short': short,
                'url': url_for('book_detail', book_id=r['id'])
            })
        return jsonify({'ok': True, 'suggestions': out})

    @app.post('/me/avatar')
    @login_required
    def upload_avatar():
        _ensure_avatar_dir()
        if 'avatar' not in request.files:
            flash('Không có file được gửi.')
            return redirect(url_for('profile'))
        f = request.files['avatar']
        if f.filename == '':
            flash('Không có file được chọn.')
            return redirect(url_for('profile'))
        filename = secure_filename(f.filename)
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext not in ALLOWED_AVATAR_EXT:
            flash('Định dạng ảnh không cho phép.')
            return redirect(url_for('profile'))
        uid = int(session['user_id'])
        _remove_existing_avatars(uid)
        out_name = f"{uid}.{ext}"
        dest = os.path.join(AVATAR_DIR, out_name)
        f.save(dest)
        flash('Đã cập nhật avatar.')
        return redirect(url_for('profile'))

    @app.post('/me/avatar/delete')
    @login_required
    def delete_avatar():
        uid = int(session['user_id'])
        _remove_existing_avatars(uid)
        flash('Đã xoá avatar.')
        return redirect(url_for('profile'))

    # ---------------- Profile & Bookmarks ----------------
    @app.route("/me")
    @login_required
    def profile():
        db = get_db()
        uid = int(session["user_id"])  # type: ignore[index]
        user = db.execute("SELECT id, username, role FROM users WHERE id=?", (uid,)).fetchone()
        bookmarks = db.execute(
            "SELECT b.id, b.title, b.author, b.cover_url FROM bookmarks m JOIN books b ON b.id=m.book_id WHERE m.user_id=? ORDER BY m.created_at DESC",
            (uid,),
        ).fetchall()
        my_reviews = db.execute(
            "SELECT r.id, r.book_id, r.reviewer, r.rating, r.created_at, b.title as book_title FROM reviews r JOIN books b ON b.id=r.book_id WHERE r.reviewer=? ORDER BY r.created_at DESC",
            (session.get("username"),),
        ).fetchall()
        return render_template("profile.html", user=user, bookmarks=bookmarks, my_reviews=my_reviews)

    @app.post("/books/<int:book_id>/bookmark")
    @login_required
    def toggle_bookmark(book_id: int):
        db = get_db()
        uid = int(session["user_id"])  # type: ignore[index]
        existed = db.execute("SELECT 1 FROM bookmarks WHERE user_id=? AND book_id=?", (uid, book_id)).fetchone()
        if existed:
            db.execute("DELETE FROM bookmarks WHERE user_id=? AND book_id=?", (uid, book_id))
            db.commit()
            flash("✅ Đã bỏ lưu sách thành công!")
        else:
            db.execute("INSERT INTO bookmarks (user_id, book_id) VALUES (?,?)", (uid, book_id))
            db.commit()
            flash("✅ Đã lưu sách vào mục yêu thích thành công!")
        return redirect(url_for("book_detail", book_id=book_id))

    

    # ---------------- Admin: Categories ----------------
    @app.route("/admin/categories")
    @admin_required
    def admin_categories():
        db = get_db()
        cats = db.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
        return render_template("admin_categories.html", categories=cats)

    @app.route("/admin/categories/new", methods=["POST"])
    @admin_required
    def admin_categories_new():
        name = (request.form.get("name") or "").strip()
        if not name:
            flash("Vui lòng nhập tên danh mục.")
            return redirect(url_for("admin_categories"))
        db = get_db()
        exists = db.execute("SELECT 1 FROM categories WHERE name=?", (name,)).fetchone()
        if exists:
            flash("Danh mục đã tồn tại.")
            return redirect(url_for("admin_categories"))
        db.execute("INSERT INTO categories (name, slug) VALUES (?,?)", (name, None))
        db.commit()
        flash("✅ Đã thêm danh mục thành công!")
        return redirect(url_for("admin_categories"))

    @app.route("/admin/categories/<int:cat_id>/delete", methods=["POST"])
    @admin_required
    def admin_categories_delete(cat_id: int):
        db = get_db()
        # detach books in this category
        db.execute("UPDATE books SET category_id=NULL WHERE category_id=?", (cat_id,))
        db.execute("DELETE FROM categories WHERE id=?", (cat_id,))
        db.commit()
        flash("✅ Đã xoá danh mục thành công!")
        return redirect(url_for("admin_categories"))

    # ---------------- Admin: Tags ----------------
    @app.route("/admin/tags")
    @admin_required
    def admin_tags():
        db = get_db()
        tags = db.execute("SELECT id, name FROM tags ORDER BY name").fetchall()
        return render_template("admin_tags.html", tags=tags)

    @app.route("/admin/tags/new", methods=["POST"])
    @admin_required
    def admin_tags_new():
        name = (request.form.get("name") or "").strip()
        if not name:
            flash("Vui lòng nhập tên tag.")
            return redirect(url_for("admin_tags"))
        db = get_db()
        exists = db.execute("SELECT 1 FROM tags WHERE name=?", (name,)).fetchone()
        if exists:
            flash("Tag đã tồn tại.")
            return redirect(url_for("admin_tags"))
        db.execute("INSERT INTO tags (name, slug) VALUES (?,?)", (name, None))
        db.commit()
        flash("✅ Đã thêm tag thành công!")
        return redirect(url_for("admin_tags"))

    @app.route("/admin/tags/<int:tag_id>/delete", methods=["POST"])
    @admin_required
    def admin_tags_delete(tag_id: int):
        db = get_db()
        db.execute("DELETE FROM book_tags WHERE tag_id=?", (tag_id,))
        db.execute("DELETE FROM tags WHERE id=?", (tag_id,))
        db.commit()
        flash("✅ Đã xoá tag thành công!")
        return redirect(url_for("admin_tags"))

    # ---------------- Admin: User Management ----------------
    @app.route("/admin/users")
    @admin_required
    def admin_users():
        db = get_db()
        # Query parameters
        q = (request.args.get("q") or "").strip()
        role_filter = (request.args.get("role") or "").strip()
        sort = request.args.get("sort") or "created_desc"
        
        where = []
        params = []
        
        if q:
            where.append("(username LIKE ?)")
            params.append(f"%{q}%")
        
        if role_filter:
            where.append("(role = ?)")
            params.append(role_filter)
        
        where_sql = (" WHERE " + " AND ".join(where)) if where else ""
        
        if sort == "username_asc":
            order_sql = " ORDER BY username COLLATE NOCASE ASC"
        elif sort == "username_desc":
            order_sql = " ORDER BY username COLLATE NOCASE DESC"
        elif sort == "id_asc":
            order_sql = " ORDER BY id ASC"
        elif sort == "id_desc":
            order_sql = " ORDER BY id DESC"
        elif sort == "role_asc":
            order_sql = " ORDER BY role ASC"
        elif sort == "role_desc":
            order_sql = " ORDER BY role DESC"
        else:
            order_sql = " ORDER BY created_at DESC"
        
        users = db.execute(
            f"SELECT id, username, password_hash, role, created_at FROM users{where_sql}{order_sql}",
            params
        ).fetchall()
        
        # Get statistics
        total_users = db.execute("SELECT COUNT(1) FROM users").fetchone()[0]
        admin_count = db.execute("SELECT COUNT(1) FROM users WHERE role='admin'").fetchone()[0]
        user_count = db.execute("SELECT COUNT(1) FROM users WHERE role='user'").fetchone()[0]
        
        return render_template("admin_users.html", 
                             users=users, 
                             q=q, 
                             role_filter=role_filter, 
                             sort=sort,
                             total_users=total_users,
                             admin_count=admin_count,
                             user_count=user_count)

    @app.route("/admin/users/<int:user_id>/delete", methods=["POST"])
    @admin_required
    def admin_users_delete(user_id: int):
        db = get_db()
        # Prevent deleting admin users
        user = db.execute("SELECT role FROM users WHERE id=?", (user_id,)).fetchone()
        if not user:
            flash("Không tìm thấy tài khoản.")
            return redirect(url_for("admin_users"))
        if user["role"] == "admin":
            flash("Không thể xóa tài khoản admin.")
            return redirect(url_for("admin_users"))
        # Delete user and related data
        db.execute("DELETE FROM bookmarks WHERE user_id=?", (user_id,))
        db.execute("DELETE FROM review_votes WHERE user_id=?", (user_id,))
        db.execute("DELETE FROM review_reports WHERE reporter_user_id=?", (user_id,))
        db.execute("DELETE FROM users WHERE id=?", (user_id,))
        db.commit()
        flash("✅ Đã xóa tài khoản thành công!")
        return redirect(url_for("admin_users"))

    # ---------------- Admin: Review Moderation ----------------
    @app.route("/admin/reviews")
    @admin_required
    def admin_reviews_queue():
        db = get_db()
        pending = db.execute(
            "SELECT r.id, r.book_id, b.title as book_title, r.reviewer, r.rating, r.created_at FROM reviews r JOIN books b ON b.id=r.book_id WHERE r.status='pending' ORDER BY r.created_at ASC"
        ).fetchall()
        return render_template("admin_reviews.html", pending=pending)

    @app.post("/admin/reviews/generate-long")
    @admin_required
    def admin_generate_long_reviews():
        """Generate long, structured sample reviews for books lacking approved reviews."""
        db = get_db()
        # find books without any approved review
        rows = db.execute(
            """
            SELECT b.id, b.title, b.author, COALESCE(b.description,'') as description, COALESCE(b.genre,'Khác') as genre
            FROM books b
            WHERE NOT EXISTS (
              SELECT 1 FROM reviews r WHERE r.book_id=b.id AND r.status='approved'
            )
            ORDER BY b.created_at DESC
            """
        ).fetchall()
        inserted = 0
        for r in rows:
            title = r["title"]
            author = r["author"]
            desc = (r["description"] or "").strip()
            genre = r["genre"]
            # build long-form markdown content
            summary = desc or f"Cuốn sách {title} của {author} thuộc thể loại {genre}. Bài review này cung cấp cái nhìn tổng quan cùng những điểm đáng chú ý."
            content = (
f"""## Tóm tắt ngắn\n\n{summary}\n\n"""
f"""## Điểm nổi bật\n\n- Bố cục mạch lạc, dễ theo dõi\n- Thông điệp rõ ràng, mang tính ứng dụng cao\n- Ngôn ngữ gần gũi, phù hợp độc giả đại chúng\n\n"""
f"""## Hạn chế\n\n- Một số chương còn lặp ý, có thể rút gọn\n- Ví dụ chưa thật sự đa dạng cho mọi bối cảnh\n\n"""
f"""## Ai nên đọc\n\n- Bạn đọc quan tâm tới thể loại {genre}\n- Người mới tìm hiểu về chủ đề của tác giả {author}\n- Độc giả cần tài liệu cô đọng để tham khảo nhanh\n\n"""
f"""## Đánh giá tổng quan\n\nTổng thể, {title} là một lựa chọn xứng đáng với thời gian đọc. Tác phẩm cân bằng giữa tính thực tiễn và chiều sâu, phù hợp để ghi chú và áp dụng vào công việc/học tập.\n"""
            )
            details = (
f"""### Phân tích chi tiết\n\n1. Cấu trúc: Tác phẩm chia thành các chương ngắn, mỗi chương giải quyết một vấn đề cụ thể.\n2. Lập luận: Tác giả sử dụng ví dụ minh họa thuyết phục, có đối chiếu dữ liệu khi cần.\n3. Giá trị tái đọc: Có thể đọc theo chương, tra cứu như sổ tay.\n\n> Trích dẫn ấn tượng: \"Điều quan trọng không phải là thời gian bạn có, mà là chất lượng sự tập trung khi sử dụng thời gian đó.\"\n\n"""
            )
            db.execute(
                "INSERT INTO reviews (book_id, reviewer, rating, content, details, status) VALUES (?,?,?,?,?,?)",
                (r["id"], "Hệ thống", 5, content, details, "approved"),
            )
            inserted += 1
        db.commit()
        flash(f"✅ Đã tạo {inserted} review mẫu dài cho các sách chưa có review thành công!")
        return redirect(url_for("admin_books"))

    @app.post("/admin/books/generate-summaries")
    @admin_required
    def admin_generate_long_summaries():
        """Generate long-form summaries for books with missing/short descriptions."""
        db = get_db()
        rows = db.execute(
            "SELECT id, title, author, COALESCE(genre,'Khác') as genre, COALESCE(description,'') as description FROM books ORDER BY id"
        ).fetchall()
        updated = 0
        for r in rows:
            desc = (r["description"] or "").strip()
            if len(desc) >= 240:
                continue
            title = r["title"]
            author = r["author"]
            genre = r["genre"]
            long_desc = (
f"""{title} là một tác phẩm thuộc thể loại {genre} do {author} chấp bút, tập trung vào việc mở rộng góc nhìn và truyền cảm hứng hành động cho người đọc. Cuốn sách triển khai nội dung theo nhịp độ rõ ràng, kết hợp giữa các câu chuyện minh họa, nguyên tắc cốt lõi và những bài học dễ áp dụng vào bối cảnh đời sống và công việc hàng ngày.\n\n"""
f"""Nội dung được sắp xếp mạch lạc theo từng chủ đề, mỗi chương gói gọn một ý tưởng trọng tâm kèm ví dụ cụ thể. Tác giả duy trì giọng văn gần gũi, nhấn mạnh tính thực tiễn hơn là lý thuyết suông, nhờ vậy độc giả có thể vừa đọc vừa ghi chú, thử nghiệm ngay với các tình huống quen thuộc. Bên cạnh đó, cuốn sách cũng đưa ra những cảnh báo về các hiểu lầm phổ biến, giúp người đọc tránh rơi vào các bẫy tư duy khi áp dụng.\n\n"""
f"""Điểm đáng giá của {title} nằm ở khả năng cân bằng giữa kiến thức và trải nghiệm: các khái niệm được diễn giải tối giản, đi kèm khuyến nghị thực hành ngắn gọn, phù hợp cả cho người mới lẫn độc giả dày dạn. Nếu bạn đang tìm một tài liệu cô đọng nhưng đủ chiều sâu để bắt đầu và theo đuổi chủ đề {genre}, {title} là lựa chọn rất đáng tham khảo."""
            )
            db.execute("UPDATE books SET description=? WHERE id=?", (long_desc, r["id"]))
            updated += 1
        db.commit()
        flash(f"Đã tạo/cập nhật tóm tắt dài cho {updated} sách.")
        return redirect(url_for("admin_books"))

    @app.post('/admin/books/<int:book_id>/enhance-description')
    @admin_required
    def admin_enhance_book_description(book_id: int):
        """Enhance a single book's description to be longer and more engaging."""
        db = get_db()
        row = db.execute("SELECT id, title, author, COALESCE(genre,'Khác') as genre, COALESCE(description,'') as description FROM books WHERE id=?", (book_id,)).fetchone()
        if not row:
            flash('Không tìm thấy sách.')
            return redirect(url_for('admin_books'))
        title = row['title']; author = row['author']; genre = row['genre']
        base = (row['description'] or '').strip()
        intro = base if len(base) > 0 else f"{title} của {author} là một tác phẩm {genre} nổi bật."
        enhanced = (
f"""{intro}\n\n"""
f"""Cuốn sách dẫn dắt người đọc đi qua từng lớp ý tưởng một cách mạch lạc, xen kẽ giữa câu chuyện, tình huống thực tiễn và các nguyên tắc cốt lõi. Tác giả giữ nhịp rất tốt: mỗi chương đều có điểm nhấn, có ví dụ dễ hình dung và lời khuyên có thể áp dụng ngay.\n\n"""
f"""Bên cạnh kiến thức, {title} còn khơi gợi cảm hứng hành động: khuyến khích bạn ghi chú, thử nghiệm, rồi quay lại đối chiếu kết quả. Nhờ vậy, trải nghiệm đọc không chỉ dừng ở mức hiểu mà còn chuyển hóa thành thay đổi nhỏ nhưng bền vững trong đời sống.\n\n"""
f"""Nếu bạn đang tìm một cuốn {genre} vừa dễ đọc vừa giàu giá trị tái đọc, {title} là lựa chọn đáng cân nhắc. Tác phẩm phù hợp cho cả người mới lẫn độc giả đã có nền tảng, muốn hệ thống lại tư duy và mở rộng góc nhìn."""
        )
        db.execute('UPDATE books SET description=? WHERE id=?', (enhanced, book_id))
        db.commit()
        flash('Đã viết lại mô tả dài và hấp dẫn hơn cho sách.')
        return redirect(url_for('admin_books_edit', book_id=book_id))

    @app.post('/admin/books/<int:book_id>/generate-review')
    @admin_required
    def admin_generate_review_for_book(book_id: int):
        db = get_db()
        row = db.execute('SELECT id, title, author, COALESCE(genre,\'Khác\') as genre, COALESCE(description,\'\') as description FROM books WHERE id=?', (book_id,)).fetchone()
        if not row:
            flash('Không tìm thấy sách.')
            return redirect(url_for('admin_books'))
        title=row['title']; author=row['author']; genre=row['genre']; desc=(row['description'] or '').strip()
        content=(
f"""## Tổng quan\n\n{title} của {author} là một đóng góp đáng chú ý trong dòng sách {genre}. Cuốn sách cân bằng giữa trải nghiệm và tri thức, giúp người đọc vừa hiểu vấn đề, vừa có công cụ áp dụng ngay.\n\n"""
f"""## Những điều cuốn hút\n\n- Cách kể chuyện gần gũi, ví dụ đời thường\n- Nguyên tắc súc tích, dễ nhớ\n- Bài tập/khuyến nghị cụ thể để thực hành\n\n"""
f"""## Điểm cần cân nhắc\n\n- Một vài đoạn có thể rút gọn để tăng nhịp đọc\n- Cần đọc kèm ghi chú để thấm sâu hơn\n\n"""
f"""## Kết luận\n\n{desc or f'Tác phẩm mang lại cảm hứng và hướng dẫn rõ ràng, phù hợp để bắt đầu và theo dõi tiến bộ trong chủ đề {genre}.'}"""
        )
        details=(
"""### Gợi ý áp dụng\n\n1) Đọc theo chương, ghi chú 3 ý chính.\n2) Thử một thay đổi nhỏ trong 24 giờ.\n3) Đánh giá kết quả sau 7 ngày và điều chỉnh.\n"""
        )
        db.execute('INSERT INTO reviews (book_id, reviewer, rating, content, details, status) VALUES (?,?,?,?,?,?)', (book_id, 'Biên tập', 5, content, details, 'approved'))
        db.commit()
        flash('Đã tạo review biên tập dài cho sách.')
        return redirect(url_for('admin_books_edit', book_id=book_id))

    @app.route("/admin/reviews/<int:review_id>/edit", methods=["GET", "POST"])
    @admin_required
    def admin_review_edit(review_id: int):
        db = get_db()
        if request.method == "POST":
            details = (request.form.get("details") or "").strip()
            status = (request.form.get("status") or "").strip() or None
            db.execute("UPDATE reviews SET details=?, moderated_at=CURRENT_TIMESTAMP, moderated_by=COALESCE(moderated_by, ?) WHERE id=?", (details or None, session.get("username"), review_id))
            if status in ("approved", "rejected", "pending"):
                db.execute("UPDATE reviews SET status=? WHERE id=?", (status, review_id))
            db.execute("INSERT INTO audit_log (action, meta) VALUES (?,?)", ("review_details_updated", f"id={review_id}"))
            db.commit()
        flash("✅ Đã cập nhật chi tiết review thành công!")
        return redirect(url_for("admin_reviews_queue"))
        row = db.execute("SELECT r.id, r.book_id, b.title as book_title, r.reviewer, r.rating, r.content, r.details, r.status FROM reviews r JOIN books b ON b.id=r.book_id WHERE r.id=?", (review_id,)).fetchone()
        if not row:
            flash("Không tìm thấy review.")
            return redirect(url_for("admin_reviews_queue"))
        return render_template("admin_review_edit.html", review=row, render_markdown=render_markdown_safe)

    @app.post("/admin/reviews/<int:review_id>/approve")
    @admin_required
    def admin_review_approve(review_id: int):
        db = get_db()
        db.execute("UPDATE reviews SET status='approved', moderated_at=CURRENT_TIMESTAMP, moderated_by=? WHERE id=?", (session.get("username"), review_id))
        db.execute("INSERT INTO audit_log (action, meta) VALUES (?,?)", ("review_approved", f"id={review_id}"))
        db.commit()
        flash("✅ Đã duyệt review thành công!")
        return redirect(url_for("admin_reviews_queue"))

    @app.post("/admin/reviews/<int:review_id>/reject")
    @admin_required
    def admin_review_reject(review_id: int):
        db = get_db()
        reason = (request.form.get("reason") or "").strip()
        db.execute("UPDATE reviews SET status='rejected', moderated_at=CURRENT_TIMESTAMP, moderated_by=?, reject_reason=? WHERE id=?", (session.get("username"), reason or None, review_id))
        db.execute("INSERT INTO audit_log (action, meta) VALUES (?,?)", ("review_rejected", f"id={review_id};reason={reason}"))
        db.commit()
        flash("✅ Đã từ chối review thành công!")
        return redirect(url_for("admin_reviews_queue"))

    # ---------------- Review interactions ----------------
    @app.post("/reviews/<int:review_id>/vote")
    def review_vote(review_id: int):
        if not session.get("user_id"):
            return jsonify({"ok": False, "error": "auth"}), 401
        db = get_db()
        user_id = int(session["user_id"])  # type: ignore[index]
        existed = db.execute("SELECT 1 FROM review_votes WHERE review_id=? AND user_id=?", (review_id, user_id)).fetchone()
        if existed:
            db.execute("DELETE FROM review_votes WHERE review_id=? AND user_id=?", (review_id, user_id))
        else:
            db.execute("INSERT INTO review_votes (review_id, user_id) VALUES (?,?)", (review_id, user_id))
        db.commit()
        count = db.execute("SELECT COUNT(1) FROM review_votes WHERE review_id=?", (review_id,)).fetchone()[0]
        return jsonify({"ok": True, "votes": count})

    @app.post("/reviews/<int:review_id>/comments")
    def review_comment_add(review_id: int):
        author = (session.get("username") or "Ẩn danh")
        content = (request.form.get("content") or "").strip()
        parent_id_raw = (request.form.get("parent_id") or "").strip()
        if not content:
            flash("Nội dung bình luận không được để trống.")
            return redirect(request.referrer or url_for("home"))
        parent_id: Optional[int] = None
        if parent_id_raw:
            try:
                parent_id = int(parent_id_raw)
            except ValueError:
                parent_id = None
        db = get_db()
        db.execute(
            "INSERT INTO review_comments (review_id, parent_id, author, content) VALUES (?,?,?,?)",
            (review_id, parent_id, author, content),
        )
        db.commit()
        return redirect(request.referrer or url_for("home"))

    @app.post("/reviews/<int:review_id>/report")
    def review_report(review_id: int):
        reason = (request.form.get("reason") or "").strip()
        user_id = session.get("user_id")
        db = get_db()
        db.execute(
            "INSERT INTO review_reports (review_id, reporter_user_id, reason) VALUES (?,?,?)",
            (review_id, user_id, reason or None),
        )
        db.commit()
        flash("✅ Đã gửi báo cáo thành công! Cảm ơn bạn!")
        return redirect(request.referrer or url_for("home"))

    # ---------------- Admin Books CRUD ----------------
    @app.route("/admin/books")
    @admin_required
    def admin_books():
        db = get_db()
        sort = (request.args.get("sort") or "").strip()
        if sort == "title_asc":
            order_sql = " ORDER BY title COLLATE NOCASE ASC"
        elif sort == "title_desc":
            order_sql = " ORDER BY title COLLATE NOCASE DESC"
        elif sort == "id_asc":
            order_sql = " ORDER BY id ASC"
        elif sort == "id_desc":
            order_sql = " ORDER BY id DESC"
        else:
            order_sql = " ORDER BY created_at DESC"

        books = db.execute(
            "SELECT id, title, author, cover_url, description, book_code FROM books" + order_sql
        ).fetchall()
        return render_template("admin_books.html", books=books)

    @app.route('/admin/seed-demo', methods=['POST'])
    @admin_required
    def admin_seed_demo():
        demo = [
            ("Harry Potter và Hòn đá Phù thủy", "J.K. Rowling", '/static/placeholder.jpg', 'Phù thủy trẻ bắt đầu hành trình.'),
            ("Nhà giả kim", "Paulo Coelho", '/static/placeholder.jpg', 'Một câu chuyện về theo đuổi ước mơ.'),
            ("Đắc nhân tâm", "Dale Carnegie", '/static/placeholder.jpg', 'Cẩm nang giao tiếp.'),
            ("Sapiens: Lược sử loài người", "Yuval Noah Harari", '/static/placeholder.jpg', 'Lược sử loài người.'),
            ("Cha giàu cha nghèo", "Robert Kiyosaki", '/static/placeholder.jpg', 'Tư duy tài chính cá nhân.'),
        ]
        db = get_db()
        cur = db.cursor()
        cur.executemany('INSERT INTO books (title, author, cover_url, description) VALUES (?,?,?,?)', demo)
        db.commit()
        flash('✅ Đã thêm sách demo thành công!')
        return redirect(url_for('admin_books'))
    @app.route('/admin/books/fix-book-codes', methods=['POST'])
    @admin_required
    def admin_fix_book_codes():
        db = get_db()
        # find books with NULL or empty book_code
        rows = db.execute("SELECT id FROM books WHERE book_code IS NULL OR book_code='' ORDER BY id").fetchall()
        updated = 0
        for r in rows:
            bid = r['id']
            # generate code BK + zero-padded id
            code = f"BK{bid:04d}"
            # ensure uniqueness
            exists = db.execute("SELECT 1 FROM books WHERE book_code=?", (code,)).fetchone()
            if exists:
                # fallback to BK + timestamp
                import time
                code = f"BK{bid}_{int(time.time())}"
            db.execute("UPDATE books SET book_code=? WHERE id=?", (code, bid))
            updated += 1
        db.commit()
        flash(f'✅ Đã cập nhật mã cho {updated} sách thành công!')
        return redirect(url_for('admin_books'))

    @app.route("/admin/books/new", methods=["GET", "POST"])
    @admin_required
    def admin_books_new():
        db = get_db()
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            author = request.form.get("author", "").strip()
            cover_url = request.form.get("cover_url", "").strip()
            
            # Handle file upload
            cover_file = request.files.get('cover_file')
            if cover_file and cover_file.filename:
                # Save uploaded file
                filename = secure_filename(cover_file.filename)
                if filename:
                    # Ensure extension
                    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
                    if ext not in ALLOWED_IMAGE_EXT:
                        ext = 'jpg'
                    # Generate unique filename
                    import time
                    unique_filename = f"book_{int(time.time())}_{filename}"
                    if '.' not in unique_filename:
                        unique_filename += f".{ext}"
                    dest_path = os.path.join(UPLOADS_DIR, unique_filename)
                    cover_file.save(dest_path)
                    cover_url = f"/static/uploads/{unique_filename}"
                    flash(f"✅ Đã upload và lưu hình ảnh: {filename}")
            elif cover_url and cover_url.strip():
                # Check if user wants to keep external URL
                keep_external = request.form.get('keep_external_url')
                if keep_external:
                    # Keep original URL without downloading
                    cover_url = cover_url.strip()
                    flash(f"✅ Đã lưu URL hình ảnh: {cover_url}")
                else:
                    # if external URL provided, attempt to download and store locally
                    try:
                        original_url = cover_url.strip()
                        cover_url = _download_cover_if_external(original_url)
                        if cover_url != original_url:
                            flash(f"✅ Đã tải và lưu hình ảnh từ URL: {original_url}")
                        else:
                            flash(f"✅ Đã lưu URL hình ảnh: {original_url}")
                    except Exception as e:
                        print(f"Error downloading cover: {e}")
                        flash(f"Không thể tải hình ảnh từ URL, đã lưu URL gốc: {cover_url}")
                        # Keep original URL if download fails
                        pass
            description = request.form.get("description", "").strip()
            genre = request.form.get("genre", "").strip()
            publisher = request.form.get("publisher", "").strip()
            num_pages_raw = request.form.get("num_pages", "").strip()
            book_code = request.form.get("book_code", "").strip()
            category_id_raw = request.form.get("category_id", "").strip()
            tags_raw = request.form.get("tags", "")
            if not title or not author:
                flash("Vui lòng nhập tiêu đề và tác giả.")
                return redirect(url_for("admin_books_new"))
            # allow empty book_code; we'll auto-generate after insert if missing
            if not book_code:
                book_code = None
            num_pages = None
            if num_pages_raw:
                try:
                    num_pages_int = int(num_pages_raw)
                    if num_pages_int < 1:
                        raise ValueError
                    num_pages = num_pages_int
                except ValueError:
                    flash("Số trang phải là số nguyên dương.")
                    return redirect(url_for("admin_books_new"))
            exists_code = db.execute("SELECT 1 FROM books WHERE book_code=?", (book_code,)).fetchone()
            if exists_code:
                flash("Mã sách (book_code) đã tồn tại, vui lòng chọn mã khác.")
                return redirect(url_for("admin_books_new"))
            category_id = None
            if category_id_raw:
                try:
                    category_id = int(category_id_raw)
                except ValueError:
                    category_id = None
            cur = db.execute(
                "INSERT INTO books (title, author, cover_url, description, genre, publisher, num_pages, book_code, category_id) VALUES (?,?,?,?,?,?,?,?,?)",
                (title, author, cover_url, description, genre or None, publisher or None, num_pages, book_code, category_id),
            )
            book_id = int(cur.lastrowid)
            # auto-generate book_code if it was None
            if not book_code:
                gen_code = f"BK{book_id:04d}"
                exists = db.execute("SELECT 1 FROM books WHERE book_code=?", (gen_code,)).fetchone()
                if exists:
                    gen_code = f"BK{book_id}_{int(time.time())}"
                db.execute("UPDATE books SET book_code=? WHERE id=?", (gen_code, book_id))
                book_code = gen_code
            tags = _parse_tags_csv(tags_raw)
            _set_book_tags(db, book_id, tags)
            db.commit()
            flash(f"✅ Đã thêm sách thành công: '{title}' của {author}")
            return redirect(url_for("admin_books"))
        # GET
        categories = db.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
        return render_template("admin_book_form.html", categories=categories)

    @app.route("/admin/books/<int:book_id>/edit", methods=["GET", "POST"])
    @admin_required
    def admin_books_edit(book_id: int):
        db = get_db()
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            author = request.form.get("author", "").strip()
            cover_url = request.form.get("cover_url", "").strip()
            
            # Handle file upload
            cover_file = request.files.get('cover_file')
            if cover_file and cover_file.filename:
                # Save uploaded file
                filename = secure_filename(cover_file.filename)
                if filename:
                    # Ensure extension
                    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
                    if ext not in ALLOWED_IMAGE_EXT:
                        ext = 'jpg'
                    # Generate unique filename
                    import time
                    unique_filename = f"book_{book_id}_{int(time.time())}_{filename}"
                    if '.' not in unique_filename:
                        unique_filename += f".{ext}"
                    dest_path = os.path.join(UPLOADS_DIR, unique_filename)
                    cover_file.save(dest_path)
                    cover_url = f"/static/uploads/{unique_filename}"
                    flash(f"✅ Đã upload và lưu hình ảnh: {filename}")
            elif cover_url and cover_url.strip():
                # Check if user wants to keep external URL
                keep_external = request.form.get('keep_external_url')
                if keep_external:
                    # Keep original URL without downloading
                    cover_url = cover_url.strip()
                    flash(f"✅ Đã lưu URL hình ảnh: {cover_url}")
                else:
                    try:
                        original_url = cover_url.strip()
                        cover_url = _download_cover_if_external(original_url)
                        if cover_url != original_url:
                            flash(f"✅ Đã tải và lưu hình ảnh từ URL: {original_url}")
                        else:
                            flash(f"✅ Đã lưu URL hình ảnh: {original_url}")
                    except Exception as e:
                        print(f"Error downloading cover: {e}")
                        flash(f"Không thể tải hình ảnh từ URL, đã lưu URL gốc: {cover_url}")
                        # Keep original URL if download fails
                        pass
            description = request.form.get("description", "").strip()
            genre = request.form.get("genre", "").strip()
            publisher = request.form.get("publisher", "").strip()
            num_pages_raw = request.form.get("num_pages", "").strip()
            book_code = request.form.get("book_code", "").strip()
            category_id_raw = request.form.get("category_id", "").strip()
            tags_raw = request.form.get("tags", "")
            if not title or not author:
                flash("Vui lòng nhập tiêu đề và tác giả.")
                return redirect(url_for("admin_books_edit", book_id=book_id))
            # allow empty book_code on edit -> auto-generate
            if not book_code:
                book_code = f"BK{book_id:04d}"
                exists_try = db.execute("SELECT 1 FROM books WHERE book_code=? AND id<>?", (book_code, book_id)).fetchone()
                if exists_try:
                    book_code = f"BK{book_id}_{int(time.time())}"
            num_pages = None
            if num_pages_raw:
                try:
                    num_pages_int = int(num_pages_raw)
                    if num_pages_int < 1:
                        raise ValueError
                    num_pages = num_pages_int
                except ValueError:
                    flash("Số trang phải là số nguyên dương.")
                    return redirect(url_for("admin_books_edit", book_id=book_id))
            exists_code = db.execute("SELECT 1 FROM books WHERE book_code=? AND id<>?", (book_code, book_id)).fetchone()
            if exists_code:
                flash("Mã sách (book_code) đã tồn tại ở sách khác.")
                return redirect(url_for("admin_books_edit", book_id=book_id))
            category_id = None
            if category_id_raw:
                try:
                    category_id = int(category_id_raw)
                except ValueError:
                    category_id = None
            db.execute(
                "UPDATE books SET title=?, author=?, cover_url=?, description=?, genre=?, publisher=?, num_pages=?, book_code=?, category_id=? WHERE id=?",
                (title, author, cover_url, description, genre or None, publisher or None, num_pages, book_code, category_id, book_id),
            )
            tags = _parse_tags_csv(tags_raw)
            _set_book_tags(db, book_id, tags)
            db.commit()
            flash(f"✅ Đã cập nhật sách thành công: '{title}' của {author}")
            return redirect(url_for("admin_books_edit", book_id=book_id))
        # GET
        book = db.execute(
            "SELECT id, title, author, cover_url, description, genre, publisher, num_pages, book_code, category_id FROM books WHERE id=?",
            (book_id,),
        ).fetchone()
        if not book:
            flash("Không tìm thấy sách.")
            return redirect(url_for("admin_books"))
        categories = db.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
        tags = db.execute(
            "SELECT t.name FROM tags t JOIN book_tags bt ON bt.tag_id=t.id WHERE bt.book_id=? ORDER BY t.name",
            (book_id,),
        ).fetchall()
        return render_template("admin_book_form.html", book=book, is_edit=True, categories=categories, tags=", ".join([r[0] for r in tags]))

    @app.route("/admin/seed", methods=["POST"])
    @admin_required
    def admin_seed_disabled():
        # Seeding disabled per user request.
        flash('Seed demo đã bị vô hiệu hóa.')
        return redirect(url_for('admin_books'))

    @app.route("/admin/books/<int:book_id>/delete", methods=["POST"])
    @admin_required
    def admin_books_delete(book_id: int):
        db = get_db()
        db.execute("DELETE FROM books WHERE id=?", (book_id,))
        db.commit()
        flash("✅ Đã xoá sách thành công!")
        return redirect(url_for("admin_books"))

    return app


def _ensure_database_exists():
    created = False
    if not os.path.exists(DB_PATH):
        schema_file = os.path.join(BASE_DIR, "schema.sql")
        if os.path.exists(schema_file):
            conn = sqlite3.connect(DB_PATH)
            with open(schema_file, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            conn.commit()
            conn.close()
            created = True

    # Seed nếu DB mới tạo hoặc trống
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(1) FROM books")
    count = cur.fetchone()[0]
    if created or count == 0:
        sample_books = [
            (
                "Atomic Habits",
                "James Clear",
                "https://images-na.ssl-images-amazon.com/images/I/51-uspgqWIL._SX329_BO1,204,203,200_.jpg",
                "Cách hình thành thói quen tốt và loại bỏ thói quen xấu bằng các bước nhỏ.",
            ),
            (
                "Deep Work",
                "Cal Newport",
                "https://images-na.ssl-images-amazon.com/images/I/41j8QX8+lfL._SX331_BO1,204,203,200_.jpg",
                "Làm việc sâu để đạt hiệu suất cao trong thế giới nhiễu loạn.",
            ),
            (
                "Clean Code",
                "Robert C. Martin",
                "https://images-na.ssl-images-amazon.com/images/I/41xShlnTZTL._SX374_BO1,204,203,200_.jpg",
                "Nguyên tắc viết mã sạch cho lập trình viên chuyên nghiệp.",
            ),
        ]
        cur.executemany(
            "INSERT INTO books (title, author, cover_url, description) VALUES (?,?,?,?)",
            sample_books,
        )
        conn.commit()
    # ensure users table exists and seed admin
    # users table with email (unique) if creating new
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'user', email TEXT UNIQUE, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
    # migrate: add genre column if not exists
    try:
        cur.execute("ALTER TABLE books ADD COLUMN genre TEXT")
        conn.commit()
    except Exception:
        pass
    # migrate: add publisher column if not exists
    try:
        cur.execute("ALTER TABLE books ADD COLUMN publisher TEXT")
        conn.commit()
    except Exception:
        pass
    # migrate: add num_pages column if not exists
    try:
        cur.execute("ALTER TABLE books ADD COLUMN num_pages INTEGER")
        conn.commit()
    except Exception:
        pass
    # migrate: add book_code column if not exists
    try:
        cur.execute("ALTER TABLE books ADD COLUMN book_code TEXT")
        conn.commit()
    except Exception:
        pass
    # add unique index on book_code if not exists
    try:
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_books_book_code ON books(book_code)")
        conn.commit()
    except Exception:
        pass
    # dynamic categories and tags schema
    cur.execute("CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, slug TEXT UNIQUE)")
    cur.execute("CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, slug TEXT UNIQUE)")
    cur.execute("CREATE TABLE IF NOT EXISTS book_tags (book_id INTEGER NOT NULL, tag_id INTEGER NOT NULL, PRIMARY KEY(book_id, tag_id), FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE, FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE)")
    # add category_id to books if not exists
    try:
        cur.execute("ALTER TABLE books ADD COLUMN category_id INTEGER REFERENCES categories(id)")
        conn.commit()
    except Exception:
        pass
    # migrate existing genres -> categories and map books.category_id
    try:
        rows = cur.execute("SELECT DISTINCT COALESCE(genre,'Khác') FROM books").fetchall()
        for (gname,) in rows:
            if not gname:
                continue
            cur.execute("INSERT OR IGNORE INTO categories (name, slug) VALUES (?,?)", (gname, None))
        conn.commit()
        # set category_id per book
        cur.execute("SELECT id, COALESCE(genre,'Khác') FROM books")
        for bid, gname in cur.fetchall():
            cat = cur.execute("SELECT id FROM categories WHERE name=?", (gname,)).fetchone()
            if cat:
                cur.execute("UPDATE books SET category_id=? WHERE id=?", (cat[0], bid))
        conn.commit()
    except Exception:
        pass
    # seed admin if not exists
    cur.execute("SELECT COUNT(1) FROM users WHERE role='admin'")
    admin_count = cur.fetchone()[0]
    if admin_count == 0:
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
            ("admin", generate_password_hash("admin123"), "admin"),
        )
        conn.commit()
    # review interactions tables
    cur.execute("CREATE TABLE IF NOT EXISTS review_votes (review_id INTEGER NOT NULL, user_id INTEGER NOT NULL, PRIMARY KEY(review_id, user_id), FOREIGN KEY(review_id) REFERENCES reviews(id) ON DELETE CASCADE)")
    cur.execute("CREATE TABLE IF NOT EXISTS review_comments (id INTEGER PRIMARY KEY AUTOINCREMENT, review_id INTEGER NOT NULL, parent_id INTEGER, author TEXT NOT NULL, content TEXT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(review_id) REFERENCES reviews(id) ON DELETE CASCADE, FOREIGN KEY(parent_id) REFERENCES review_comments(id) ON DELETE CASCADE)")
    cur.execute("CREATE TABLE IF NOT EXISTS review_reports (id INTEGER PRIMARY KEY AUTOINCREMENT, review_id INTEGER NOT NULL, reporter_user_id INTEGER, reason TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(review_id) REFERENCES reviews(id) ON DELETE CASCADE)")
    # bookmarks
    cur.execute("CREATE TABLE IF NOT EXISTS bookmarks (user_id INTEGER NOT NULL, book_id INTEGER NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(user_id, book_id), FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE)")
    # moderation fields on reviews
    try:
        cur.execute("ALTER TABLE reviews ADD COLUMN status TEXT DEFAULT 'approved'")
        conn.commit()
    except Exception:
        pass
    # add details column if not exists
    try:
        cur.execute("ALTER TABLE reviews ADD COLUMN details TEXT")
        conn.commit()
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE reviews ADD COLUMN moderated_at DATETIME")
        conn.commit()
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE reviews ADD COLUMN moderated_by TEXT")
        conn.commit()
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE reviews ADD COLUMN reject_reason TEXT")
        conn.commit()
    except Exception:
        pass
    # audit log
    cur.execute("CREATE TABLE IF NOT EXISTS audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL, meta TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
    conn.close()


if __name__ == "__main__":
    _ensure_database_exists()
    app = create_app()
    app.run(debug=True)


