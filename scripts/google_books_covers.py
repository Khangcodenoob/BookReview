#!/usr/bin/env python3
"""
Script lấy hình ảnh bìa sách thực tế từ Google Books API
"""

import os
import sqlite3
import requests
import time
import json

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
    """Tải hình ảnh từ URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=15, headers=headers)
        if response.status_code == 200 and len(response.content) > 1000:
            filepath = os.path.join(UPLOADS_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Lỗi tải {url}: {e}")
    return False

def search_google_books(title: str, author: str = "") -> str:
    """Tìm kiếm sách trên Google Books API"""
    try:
        query = f"{title} {author}".strip()
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                book = data['items'][0]
                volume_info = book.get('volumeInfo', {})
                
                # Lấy hình ảnh bìa sách
                image_links = volume_info.get('imageLinks', {})
                if image_links:
                    # Thử lấy hình ảnh lớn nhất
                    for size in ['large', 'medium', 'small', 'thumbnail']:
                        if size in image_links:
                            return image_links[size]
        
        return None
    except Exception as e:
        print(f"Lỗi tìm kiếm Google Books: {e}")
        return None

def get_db_connection():
    """Tạo kết nối database"""
    return sqlite3.connect(DB_PATH)

def update_real_book_covers():
    """Cập nhật hình ảnh bìa sách thực tế từ Google Books"""
    
    try:
        ensure_uploads_dir()
        db = get_db_connection()
        
        # Lấy tất cả sách từ database
        cursor = db.execute("SELECT id, title, author, genre, cover_url FROM books")
        books = cursor.fetchall()
        
        updated_count = 0
        
        for book_id, title, author, genre, current_cover in books:
            print(f"🔍 Tìm kiếm hình ảnh cho: {title} - {author}")
            
            # Tìm kiếm trên Google Books
            cover_url = search_google_books(title, author)
            
            if cover_url:
                # Tạo tên file
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"google_{book_id:04d}_{safe_title.replace(' ', '_')[:20]}.jpg"
                
                print(f"🔄 Đang tải hình ảnh từ Google Books...")
                
                if download_image(cover_url, filename):
                    # Cập nhật database
                    new_cover_url = f"/static/uploads/{filename}"
                    db.execute("UPDATE books SET cover_url = ? WHERE id = ?", (new_cover_url, book_id))
                    updated_count += 1
                    print(f"✅ Đã cập nhật: {title}")
                else:
                    print(f"❌ Không thể tải hình ảnh cho: {title}")
            else:
                print(f"⚠️ Không tìm thấy hình ảnh cho: {title}")
            
            time.sleep(2)  # Nghỉ để tránh spam API
        
        db.commit()
        print(f"\n🎉 Hoàn thành! Đã cập nhật {updated_count} hình ảnh bìa sách thực tế.")
        
        # Thống kê
        cursor = db.execute("SELECT COUNT(*) FROM books WHERE cover_url LIKE '/static/uploads/google_%'")
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
    print("🚀 Bắt đầu tìm kiếm hình ảnh bìa sách thực tế từ Google Books...")
    update_real_book_covers()
    print("✨ Hoàn thành!")
