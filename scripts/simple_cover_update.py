#!/usr/bin/env python3
"""
Script đơn giản để cập nhật hình ảnh bìa sách
"""

import os
import sqlite3
import requests
import time
from typing import Optional

# Đường dẫn database
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "books.db")
UPLOADS_DIR = os.path.join(BASE_DIR, "static", "uploads")

def ensure_uploads_dir():
    """Đảm bảo thư mục uploads tồn tại"""
    try:
        os.makedirs(UPLOADS_DIR, exist_ok=True)
    except Exception:
        pass

def download_image(url: str, filename: str) -> bool:
    """Tải hình ảnh từ URL và lưu vào thư mục uploads"""
    try:
        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        if response.status_code == 200 and len(response.content) > 1000:  # Đảm bảo có nội dung
            filepath = os.path.join(UPLOADS_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Lỗi tải hình ảnh {url}: {e}")
    return False

def get_db_connection():
    """Tạo kết nối database"""
    return sqlite3.connect(DB_PATH)

def update_book_covers():
    """Cập nhật hình ảnh bìa sách"""
    
    # Hình ảnh placeholder đẹp theo thể loại
    genre_covers = {
        "Tiểu thuyết": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop&crop=center",
        "Kinh tế": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=300&h=400&fit=crop&crop=center",
        "Khoa học": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop&crop=center",
        "Tâm lý": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=300&h=400&fit=crop&crop=center",
        "Văn học": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop&crop=center",
        "Lịch sử": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop&crop=center",
        "Thiếu nhi": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop&crop=center",
        "Khác": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop&crop=center"
    }
    
    try:
        ensure_uploads_dir()
        db = get_db_connection()
        
        # Lấy tất cả sách từ database
        cursor = db.execute("SELECT id, title, genre, cover_url FROM books")
        books = cursor.fetchall()
        
        updated_count = 0
        
        for book_id, title, genre, current_cover in books:
            # Bỏ qua nếu đã có hình ảnh thực
            if current_cover and current_cover != "/static/placeholder.jpg" and "uploads" in current_cover:
                print(f"⏭️ Bỏ qua (đã có hình): {title}")
                continue
                
            # Lấy URL hình ảnh theo thể loại
            cover_url = genre_covers.get(genre, genre_covers["Khác"])
            
            # Tạo tên file
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{book_id}_{safe_title.replace(' ', '_')[:20]}.jpg"
            
            # Tải hình ảnh
            print(f"🔄 Đang tải hình ảnh cho: {title} ({genre})")
            if download_image(cover_url, filename):
                # Cập nhật database
                new_cover_url = f"/static/uploads/{filename}"
                db.execute("UPDATE books SET cover_url = ? WHERE id = ?", (new_cover_url, book_id))
                updated_count += 1
                print(f"✅ Đã cập nhật: {title}")
            else:
                # Sử dụng placeholder mặc định
                db.execute("UPDATE books SET cover_url = ? WHERE id = ?", ("/static/placeholder.jpg", book_id))
                print(f"⚠️ Sử dụng placeholder cho: {title}")
            
            # Nghỉ một chút để tránh spam
            time.sleep(1)
        
        db.commit()
        print(f"\n🎉 Hoàn thành! Đã cập nhật {updated_count} hình ảnh bìa sách.")
        
        # Thống kê
        cursor = db.execute("SELECT COUNT(*) FROM books WHERE cover_url LIKE '/static/uploads/%'")
        books_with_covers = cursor.fetchone()[0]
        cursor = db.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]
        
        print(f"📊 Thống kê:")
        print(f"   - Tổng số sách: {total_books}")
        print(f"   - Sách có hình ảnh tải về: {books_with_covers}")
        print(f"   - Sách dùng placeholder: {total_books - books_with_covers}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("🚀 Bắt đầu cập nhật hình ảnh bìa sách...")
    update_book_covers()
    print("✨ Hoàn thành!")

