#!/usr/bin/env python3
"""
Script cập nhật URL hình ảnh bìa sách
"""

import os
import sqlite3

# Đường dẫn database
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "books.db")

def get_db_connection():
    """Tạo kết nối database"""
    return sqlite3.connect(DB_PATH)

def update_book_covers():
    """Cập nhật URL hình ảnh bìa sách"""
    
    # Danh sách URL hình ảnh đẹp từ Unsplash
    book_covers = {
        # Tiểu thuyết
        "Những người khốn khổ": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop&crop=center",
        "Chiến tranh và Hòa bình": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop&crop=center",
        "Bố già": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop&crop=center",
        "1984": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop&crop=center",
        "Chúa tể những chiếc nhẫn": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop&crop=center",
        
        # Kinh tế
        "Nghĩ giàu và làm giàu": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=300&h=400&fit=crop&crop=center",
        "Tư duy nhanh và chậm": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=300&h=400&fit=crop&crop=center",
        "Freakonomics": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=300&h=400&fit=crop&crop=center",
        "Rich Dad Poor Dad": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=300&h=400&fit=crop&crop=center",
        "The Lean Startup": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=300&h=400&fit=crop&crop=center",
        
        # Khoa học
        "Lược sử thời gian": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop&crop=center",
        "Sapiens": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop&crop=center",
        "Cosmos": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop&crop=center",
        "The Selfish Gene": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop&crop=center",
        "A Brief History of Time": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop&crop=center",
        
        # Tâm lý
        "Tư duy tích cực": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=300&h=400&fit=crop&crop=center",
        "Emotional Intelligence": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=300&h=400&fit=crop&crop=center",
        "The Power of Now": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=300&h=400&fit=crop&crop=center",
        "Man's Search for Meaning": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=300&h=400&fit=crop&crop=center",
        "Thinking, Fast and Slow": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=300&h=400&fit=crop&crop=center",
        
        # Văn học
        "Truyện Kiều": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop&crop=center",
        "Nhật ký trong tù": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop&crop=center",
        "Dế Mèn phiêu lưu ký": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop&crop=center",
        "Số đỏ": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop&crop=center",
        "Chí Phèo": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop&crop=center",
        
        # Lịch sử
        "Lịch sử Việt Nam": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop&crop=center",
        "The Art of War": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop&crop=center",
        "Guns, Germs, and Steel": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop&crop=center",
        "The Rise and Fall of the Third Reich": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop&crop=center",
        "A People's History of the United States": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop&crop=center",
        
        # Thiếu nhi
        "Harry Potter và Hòn đá Phù thủy": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop&crop=center",
        "Alice ở xứ sở thần tiên": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop&crop=center",
        "Peter Pan": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop&crop=center",
        "The Little Prince": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop&crop=center",
        "Winnie-the-Pooh": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop&crop=center",
        
        # Sách cũ
        "Atomic Habits": "https://images-na.ssl-images-amazon.com/images/I/51-uspgqWIL._SX329_BO1,204,203,200_.jpg",
        "Deep Work": "https://images-na.ssl-images-amazon.com/images/I/41j8QX8+lfL._SX331_BO1,204,203,200_.jpg",
        "Clean Code": "https://images-na.ssl-images-amazon.com/images/I/41xShlnTZTL._SX374_BO1,204,203,200_.jpg",
    }
    
    # Hình ảnh mặc định theo thể loại
    genre_defaults = {
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
        db = get_db_connection()
        
        # Lấy tất cả sách từ database
        cursor = db.execute("SELECT id, title, genre, cover_url FROM books")
        books = cursor.fetchall()
        
        updated_count = 0
        
        for book_id, title, genre, current_cover in books:
            # Bỏ qua nếu đã có hình ảnh thực
            if current_cover and current_cover != "/static/placeholder.jpg":
                print(f"⏭️ Bỏ qua (đã có hình): {title}")
                continue
                
            # Tìm URL hình ảnh cho sách này
            cover_url = book_covers.get(title)
            
            # Nếu không có URL cụ thể, sử dụng mặc định theo thể loại
            if not cover_url:
                cover_url = genre_defaults.get(genre, genre_defaults["Khác"])
            
            # Cập nhật database
            db.execute("UPDATE books SET cover_url = ? WHERE id = ?", (cover_url, book_id))
            updated_count += 1
            print(f"✅ Đã cập nhật: {title} ({genre})")
        
        db.commit()
        print(f"\n🎉 Hoàn thành! Đã cập nhật {updated_count} hình ảnh bìa sách.")
        
        # Thống kê
        cursor = db.execute("SELECT COUNT(*) FROM books WHERE cover_url != '/static/placeholder.jpg'")
        books_with_covers = cursor.fetchone()[0]
        cursor = db.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]
        
        print(f"📊 Thống kê:")
        print(f"   - Tổng số sách: {total_books}")
        print(f"   - Sách có hình ảnh: {books_with_covers}")
        print(f"   - Sách dùng placeholder: {total_books - books_with_covers}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("🚀 Bắt đầu cập nhật URL hình ảnh bìa sách...")
    update_book_covers()
    print("✨ Hoàn thành!")

