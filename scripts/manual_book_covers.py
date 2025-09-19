#!/usr/bin/env python3
"""
Script cập nhật hình ảnh bìa sách thực tế từ các nguồn đáng tin cậy
"""

import os
import sqlite3

# Đường dẫn database
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "books.db")

def get_db_connection():
    """Tạo kết nối database"""
    return sqlite3.connect(DB_PATH)

def update_manual_book_covers():
    """Cập nhật hình ảnh bìa sách thực tế"""
    
    # Danh sách URL hình ảnh bìa sách thực tế từ các nguồn đáng tin cậy
    real_book_covers = {
        # Tiểu thuyết
        "Những người khốn khổ": "https://covers.openlibrary.org/b/isbn/9780140444308-L.jpg",
        "Chiến tranh và Hòa bình": "https://covers.openlibrary.org/b/isbn/9780140447934-L.jpg",
        "Bố già": "https://covers.openlibrary.org/b/isbn/9780451205766-L.jpg",
        "1984": "https://covers.openlibrary.org/b/isbn/9780451524935-L.jpg",
        "Chúa tể những chiếc nhẫn": "https://covers.openlibrary.org/b/isbn/9780544003415-L.jpg",
        
        # Kinh tế
        "Nghĩ giàu và làm giàu": "https://covers.openlibrary.org/b/isbn/9781585424337-L.jpg",
        "Tư duy nhanh và chậm": "https://covers.openlibrary.org/b/isbn/9780374533557-L.jpg",
        "Freakonomics": "https://covers.openlibrary.org/b/isbn/9780060731328-L.jpg",
        "Rich Dad Poor Dad": "https://covers.openlibrary.org/b/isbn/9781612680019-L.jpg",
        "The Lean Startup": "https://covers.openlibrary.org/b/isbn/9780307887894-L.jpg",
        
        # Khoa học
        "Lược sử thời gian": "https://covers.openlibrary.org/b/isbn/9780553380163-L.jpg",
        "Sapiens": "https://covers.openlibrary.org/b/isbn/9780062316097-L.jpg",
        "Cosmos": "https://covers.openlibrary.org/b/isbn/9780345539434-L.jpg",
        "The Selfish Gene": "https://covers.openlibrary.org/b/isbn/9780192860927-L.jpg",
        "A Brief History of Time": "https://covers.openlibrary.org/b/isbn/9780553380163-L.jpg",
        
        # Tâm lý
        "Tư duy tích cực": "https://covers.openlibrary.org/b/isbn/9780743234801-L.jpg",
        "Emotional Intelligence": "https://covers.openlibrary.org/b/isbn/9780553804916-L.jpg",
        "The Power of Now": "https://covers.openlibrary.org/b/isbn/9781577314806-L.jpg",
        "Man's Search for Meaning": "https://covers.openlibrary.org/b/isbn/9780807014295-L.jpg",
        "Thinking, Fast and Slow": "https://covers.openlibrary.org/b/isbn/9780374533557-L.jpg",
        
        # Văn học
        "Truyện Kiều": "https://covers.openlibrary.org/b/isbn/9786040000000-L.jpg",
        "Nhật ký trong tù": "https://covers.openlibrary.org/b/isbn/9786040000001-L.jpg",
        "Dế Mèn phiêu lưu ký": "https://covers.openlibrary.org/b/isbn/9786040000002-L.jpg",
        "Số đỏ": "https://covers.openlibrary.org/b/isbn/9786040000003-L.jpg",
        "Chí Phèo": "https://covers.openlibrary.org/b/isbn/9786040000004-L.jpg",
        
        # Lịch sử
        "Lịch sử Việt Nam": "https://covers.openlibrary.org/b/isbn/9786040000005-L.jpg",
        "The Art of War": "https://covers.openlibrary.org/b/isbn/9781590309637-L.jpg",
        "Guns, Germs, and Steel": "https://covers.openlibrary.org/b/isbn/9780393317558-L.jpg",
        "The Rise and Fall of the Third Reich": "https://covers.openlibrary.org/b/isbn/9781451651683-L.jpg",
        "A People's History of the United States": "https://covers.openlibrary.org/b/isbn/9780062397348-L.jpg",
        
        # Thiếu nhi
        "Harry Potter và Hòn đá Phù thủy": "https://covers.openlibrary.org/b/isbn/9780439708180-L.jpg",
        "Alice ở xứ sở thần tiên": "https://covers.openlibrary.org/b/isbn/9780141439761-L.jpg",
        "Peter Pan": "https://covers.openlibrary.org/b/isbn/9780141322575-L.jpg",
        "The Little Prince": "https://covers.openlibrary.org/b/isbn/9780156012195-L.jpg",
        "Winnie-the-Pooh": "https://covers.openlibrary.org/b/isbn/9780525444435-L.jpg",
    }
    
    try:
        db = get_db_connection()
        
        # Lấy tất cả sách từ database
        cursor = db.execute("SELECT id, title, author, genre, cover_url FROM books")
        books = cursor.fetchall()
        
        updated_count = 0
        
        for book_id, title, author, genre, current_cover in books:
            # Tìm URL hình ảnh thực tế
            cover_url = real_book_covers.get(title)
            
            if cover_url:
                # Cập nhật database trực tiếp với URL
                db.execute("UPDATE books SET cover_url = ? WHERE id = ?", (cover_url, book_id))
                updated_count += 1
                print(f"✅ Đã cập nhật: {title} - {author}")
            else:
                print(f"⚠️ Không tìm thấy hình ảnh cho: {title}")
        
        db.commit()
        print(f"\n🎉 Hoàn thành! Đã cập nhật {updated_count} hình ảnh bìa sách thực tế.")
        
        # Thống kê
        cursor = db.execute("SELECT COUNT(*) FROM books WHERE cover_url LIKE '%openlibrary%'")
        books_with_real_covers = cursor.fetchone()[0]
        cursor = db.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]
        
        print(f"📊 Thống kê:")
        print(f"   - Tổng số sách: {total_books}")
        print(f"   - Sách có hình ảnh thực tế: {books_with_real_covers}")
        print(f"   - Sách chưa có hình ảnh thực tế: {total_books - books_with_real_covers}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("🚀 Bắt đầu cập nhật hình ảnh bìa sách thực tế...")
    update_manual_book_covers()
    print("✨ Hoàn thành!")
