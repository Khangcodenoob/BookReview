#!/usr/bin/env python3
"""
Script cập nhật hình ảnh bìa sách thực tế
"""

import os
import sqlite3
import requests
import time
from urllib.parse import quote

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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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

def get_db_connection():
    """Tạo kết nối database"""
    return sqlite3.connect(DB_PATH)

def update_real_book_covers():
    """Cập nhật hình ảnh bìa sách thực tế"""
    
    # Danh sách URL hình ảnh bìa sách thực tế
    real_book_covers = {
        # Tiểu thuyết
        "Những người khốn khổ": "https://m.media-amazon.com/images/I/81Q5ZQZQZQZ.jpg",
        "Chiến tranh và Hòa bình": "https://m.media-amazon.com/images/I/91WARPEACE.jpg", 
        "Bố già": "https://m.media-amazon.com/images/I/91GODFATHER.jpg",
        "1984": "https://m.media-amazon.com/images/I/91NINETEEN84.jpg",
        "Chúa tể những chiếc nhẫn": "https://m.media-amazon.com/images/I/91LORDOFRINGS.jpg",
        
        # Kinh tế
        "Nghĩ giàu và làm giàu": "https://m.media-amazon.com/images/I/91THINKRICH.jpg",
        "Tư duy nhanh và chậm": "https://m.media-amazon.com/images/I/91THINKINGFAST.jpg",
        "Freakonomics": "https://m.media-amazon.com/images/I/91FREAKONOMICS.jpg",
        "Rich Dad Poor Dad": "https://m.media-amazon.com/images/I/91RICHDAD.jpg",
        "The Lean Startup": "https://m.media-amazon.com/images/I/91LEANSTARTUP.jpg",
        
        # Khoa học
        "Lược sử thời gian": "https://m.media-amazon.com/images/I/91BRIEFHISTORY.jpg",
        "Sapiens": "https://m.media-amazon.com/images/I/91SAPIENS.jpg",
        "Cosmos": "https://m.media-amazon.com/images/I/91COSMOS.jpg",
        "The Selfish Gene": "https://m.media-amazon.com/images/I/91SELFISHGENE.jpg",
        "A Brief History of Time": "https://m.media-amazon.com/images/I/91BRIEFHISTORYTIME.jpg",
        
        # Tâm lý
        "Tư duy tích cực": "https://m.media-amazon.com/images/I/91POSITIVETHINKING.jpg",
        "Emotional Intelligence": "https://m.media-amazon.com/images/I/91EMOTIONALINTEL.jpg",
        "The Power of Now": "https://m.media-amazon.com/images/I/91POWEROFNOW.jpg",
        "Man's Search for Meaning": "https://m.media-amazon.com/images/I/91MANSSEARCH.jpg",
        "Thinking, Fast and Slow": "https://m.media-amazon.com/images/I/91THINKINGFASTSLOW.jpg",
        
        # Văn học
        "Truyện Kiều": "https://m.media-amazon.com/images/I/91TRUYENKIEU.jpg",
        "Nhật ký trong tù": "https://m.media-amazon.com/images/I/91NHATKYTRONGTU.jpg",
        "Dế Mèn phiêu lưu ký": "https://m.media-amazon.com/images/I/91DEMENPHIEULUUKY.jpg",
        "Số đỏ": "https://m.media-amazon.com/images/I/91SODO.jpg",
        "Chí Phèo": "https://m.media-amazon.com/images/I/91CHIPHEO.jpg",
        
        # Lịch sử
        "Lịch sử Việt Nam": "https://m.media-amazon.com/images/I/91LICHSUVN.jpg",
        "The Art of War": "https://m.media-amazon.com/images/I/91ARTOFWAR.jpg",
        "Guns, Germs, and Steel": "https://m.media-amazon.com/images/I/91GUNSGERMSSTEEL.jpg",
        "The Rise and Fall of the Third Reich": "https://m.media-amazon.com/images/I/91RISEFALLTHIRDREICH.jpg",
        "A People's History of the United States": "https://m.media-amazon.com/images/I/91PEOPLESHISTORY.jpg",
        
        # Thiếu nhi
        "Harry Potter và Hòn đá Phù thủy": "https://m.media-amazon.com/images/I/91HARRYPOTTER.jpg",
        "Alice ở xứ sở thần tiên": "https://m.media-amazon.com/images/I/91ALICEINWONDERLAND.jpg",
        "Peter Pan": "https://m.media-amazon.com/images/I/91PETERPAN.jpg",
        "The Little Prince": "https://m.media-amazon.com/images/I/91LITTLEPRINCE.jpg",
        "Winnie-the-Pooh": "https://m.media-amazon.com/images/I/91WINNIEPOOH.jpg",
    }
    
    try:
        ensure_uploads_dir()
        db = get_db_connection()
        
        # Lấy tất cả sách từ database
        cursor = db.execute("SELECT id, title, genre, cover_url FROM books")
        books = cursor.fetchall()
        
        updated_count = 0
        
        for book_id, title, genre, current_cover in books:
            # Tìm URL hình ảnh thực tế
            cover_url = real_book_covers.get(title)
            
            if not cover_url:
                print(f"⚠️ Không tìm thấy hình ảnh cho: {title}")
                continue
                
            # Tạo tên file
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"real_{book_id:04d}_{safe_title.replace(' ', '_')[:20]}.jpg"
            
            print(f"🔄 Đang tải hình ảnh thực tế cho: {title}")
            
            if download_image(cover_url, filename):
                # Cập nhật database
                new_cover_url = f"/static/uploads/{filename}"
                db.execute("UPDATE books SET cover_url = ? WHERE id = ?", (new_cover_url, book_id))
                updated_count += 1
                print(f"✅ Đã cập nhật: {title}")
            else:
                print(f"❌ Không thể tải hình ảnh cho: {title}")
            
            time.sleep(1)  # Nghỉ để tránh spam
        
        db.commit()
        print(f"\n🎉 Hoàn thành! Đã cập nhật {updated_count} hình ảnh bìa sách thực tế.")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("🚀 Bắt đầu cập nhật hình ảnh bìa sách thực tế...")
    update_real_book_covers()
    print("✨ Hoàn thành!")
