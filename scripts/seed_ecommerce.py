"""
Seed script for e-commerce: categories + sample books with price, stock, cover.
Run: python scripts/seed_ecommerce.py
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

import sqlite3
from pathlib import Path

DB_PATH = Path(BASE_DIR) / "books.db"

CATEGORIES = [
    ("Tiểu thuyết", "tieu-thuyet"),
    ("Kinh tế", "kinh-te"),
    ("Khoa học", "khoa-hoc"),
    ("Tâm lý", "tam-ly"),
    ("Văn học", "van-hoc"),
    ("Thiếu nhi", "thieu-nhi"),
    ("Lịch sử", "lich-su"),
    ("Khác", "khac"),
]

SAMPLE_BOOKS = [
    ("Đắc Nhân Tâm", "Dale Carnegie", "Tiểu thuyết", 89000, 50, "Cuốn sách kinh điển về nghệ thuật giao tiếp."),
    ("Tư duy nhanh và chậm", "Daniel Kahneman", "Kinh tế", 159000, 30, "Khám phá hai hệ thống tư duy của con người."),
    ("Sapiens", "Yuval Noah Harari", "Lịch sử", 179000, 25, "Lịch sử loài người từ thời tiền sử."),
    ("Atomic Habits", "James Clear", "Tâm lý", 119000, 40, "Xây dựng thói quen tốt từ những việc nhỏ."),
    ("Nhà giả kim", "Paulo Coelho", "Văn học", 69000, 60, "Hành trình tìm kiếm kho báu và ý nghĩa cuộc sống."),
    ("Lược sử thời gian", "Stephen Hawking", "Khoa học", 129000, 20, "Vũ trụ, lỗ đen và nguồn gốc."),
    ("Dế Mèn phiêu lưu ký", "Tô Hoài", "Thiếu nhi", 45000, 80, "Câu chuyện phiêu lưu của chú dế mèn."),
    ("Bố già", "Mario Puzo", "Tiểu thuyết", 99000, 35, "Thế giới mafia Mỹ."),
    ("Rich Dad Poor Dad", "Robert Kiyosaki", "Kinh tế", 99000, 45, "Tư duy tài chính và đầu tư."),
    ("Đọc vị bất kỳ ai", "David J. Lieberman", "Tâm lý", 79000, 55, "Nghệ thuật thấu hiểu người khác."),
    ("Cha giàu cha nghèo", "Robert Kiyosaki", "Kinh tế", 89000, 40, "Dạy con về tiền bạc."),
    ("Hạt giống tâm hồn", "Nhiều tác giả", "Văn học", 59000, 70, "Tuyển tập truyện ngắn ý nghĩa."),
    ("Totto-chan bên cửa sổ", "Kuroyanagi Tetsuko", "Thiếu nhi", 69000, 50, "Câu chuyện về một ngôi trường đặc biệt."),
    ("Sức mạnh của thói quen", "Charles Duhigg", "Tâm lý", 109000, 38, "Khoa học về thói quen."),
    ("Khởi nghiệp tinh gọn", "Eric Ries", "Kinh tế", 139000, 28, "Phương pháp khởi nghiệp hiệu quả."),
    ("Harry Potter và Hòn đá phù thủy", "J.K. Rowling", "Thiếu nhi", 99000, 65, "Chuyến phiêu lưu đầu tiên của Harry."),
    ("Người giàu có nhất thành Babylon", "George S. Clason", "Kinh tế", 69000, 42, "Bí quyết làm giàu từ xưa."),
    ("Đời ngắn đừng ngủ dài", "Robin Sharma", "Tâm lý", 79000, 48, "Sống có ý nghĩa mỗi ngày."),
    ("Những tấm lòng cao cả", "Edmondo De Amicis", "Văn học", 59000, 55, "Câu chuyện về tình thầy trò."),
    ("Lịch sử Việt Nam", "Nhiều tác giả", "Lịch sử", 149000, 22, "Tổng quan lịch sử dân tộc."),
    ("Deep Work", "Cal Newport", "Tâm lý", 119000, 30, "Làm việc sâu để đạt hiệu suất cao."),
    ("Clean Code", "Robert C. Martin", "Khoa học", 159000, 25, "Nguyên tắc viết mã sạch."),
    ("Chuyện con mèo dạy hải âu bay", "Luis Sepulveda", "Thiếu nhi", 69000, 45, "Bài học về tình yêu thương."),
    ("Nghệ thuật tinh tế của việc đếch quan tâm", "Mark Manson", "Tâm lý", 99000, 52, "Cách sống không lo lắng."),
    ("Cà phê cùng Tony", "Tony Buổi Sáng", "Kinh tế", 69000, 60, "Chia sẻ về khởi nghiệp và cuộc sống."),
    ("Đại gia Gatsby", "F. Scott Fitzgerald", "Văn học", 79000, 35, "Giấc mơ Mỹ và sự phù phiếm."),
    ("Bí mật của may mắn", "Alex Rovira", "Tâm lý", 59000, 48, "Cách tạo ra may mắn."),
    ("Thiên tài bên trái, kẻ điên bên phải", "Cao Minh", "Tâm lý", 89000, 40, "Ranh giới giữa thiên tài và điên loạn."),
    ("Sông Đông êm đềm", "Mikhail Sholokhov", "Văn học", 199000, 15, "Bộ tiểu thuyết sử thi Nga."),
    ("Những người khốn khổ", "Victor Hugo", "Văn học", 129000, 28, "Câu chuyện về Jean Valjean."),
]


def main():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}. Run the app first to create it.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Ensure e-commerce columns exist
    for col, sql in [
        ("price", "ALTER TABLE books ADD COLUMN price REAL DEFAULT 0"),
        ("stock", "ALTER TABLE books ADD COLUMN stock INTEGER DEFAULT 0"),
        ("isbn", "ALTER TABLE books ADD COLUMN isbn TEXT"),
        ("is_active", "ALTER TABLE books ADD COLUMN is_active INTEGER DEFAULT 1"),
    ]:
        try:
            cols = [c[1] for c in cur.execute("PRAGMA table_info(books)").fetchall()]
            if col not in cols:
                cur.execute(sql)
                conn.commit()
        except Exception:
            pass

    # Seed categories
    for name, slug in CATEGORIES:
        cur.execute("INSERT OR IGNORE INTO categories (name, slug) VALUES (?, ?)", (name, slug))
    conn.commit()

    # Get category id by name
    def get_cat_id(name):
        row = cur.execute("SELECT id FROM categories WHERE name=?", (name,)).fetchone()
        return row[0] if row else None

    # Seed books
    added = 0
    for title, author, genre, price, stock, desc in SAMPLE_BOOKS:
        cat_id = get_cat_id(genre)
        existing = cur.execute("SELECT id FROM books WHERE title=? AND author=?", (title, author)).fetchone()
        if existing:
            cur.execute(
                "UPDATE books SET price=?, stock=?, is_active=1, category_id=? WHERE id=?",
                (price, stock, cat_id, existing[0]),
            )
        else:
            cur.execute(
                """INSERT INTO books (title, author, description, genre, category_id, price, stock, is_active)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
                (title, author, desc, genre, cat_id, price, stock),
            )
            added += 1
    conn.commit()

    print(f"Seed e-commerce: {len(CATEGORIES)} categories, {added} new books added, {len(SAMPLE_BOOKS) - added} updated.")
    conn.close()


if __name__ == "__main__":
    main()
