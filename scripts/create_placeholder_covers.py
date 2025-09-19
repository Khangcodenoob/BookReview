#!/usr/bin/env python3
"""
Script tạo hình ảnh placeholder đẹp cho sách
"""

import os
import sqlite3
from PIL import Image, ImageDraw, ImageFont
import random

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

def create_book_cover(title: str, genre: str, book_id: int) -> str:
    """Tạo hình ảnh bìa sách đẹp"""
    
    # Màu sắc theo thể loại
    genre_colors = {
        "Tiểu thuyết": ["#8B4513", "#A0522D", "#D2691E"],
        "Kinh tế": ["#2E8B57", "#3CB371", "#20B2AA"],
        "Khoa học": ["#4169E1", "#6495ED", "#87CEEB"],
        "Tâm lý": ["#9370DB", "#BA55D3", "#DA70D6"],
        "Văn học": ["#B22222", "#DC143C", "#FF6347"],
        "Lịch sử": ["#8B4513", "#A0522D", "#D2691E"],
        "Thiếu nhi": ["#FF69B4", "#FFB6C1", "#FFC0CB"],
        "Khác": ["#696969", "#808080", "#A9A9A9"]
    }
    
    # Lấy màu cho thể loại
    colors = genre_colors.get(genre, genre_colors["Khác"])
    bg_color = random.choice(colors)
    
    # Tạo hình ảnh
    width, height = 300, 400
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Thêm gradient effect
    for y in range(height):
        alpha = int(255 * (1 - y / height * 0.3))
        color = tuple(int(c * alpha / 255) for c in Image.new('RGB', (1, 1), bg_color).getpixel((0, 0)))
        draw.line([(0, y), (width, y)], fill=color)
    
    # Thêm border
    draw.rectangle([0, 0, width-1, height-1], outline="#FFFFFF", width=3)
    
    # Thêm icon theo thể loại
    icons = {
        "Tiểu thuyết": "📚",
        "Kinh tế": "💰",
        "Khoa học": "🔬",
        "Tâm lý": "🧠",
        "Văn học": "✍️",
        "Lịch sử": "🏛️",
        "Thiếu nhi": "🎈",
        "Khác": "📖"
    }
    
    icon = icons.get(genre, "📖")
    
    # Vẽ icon (sử dụng text vì PIL không hỗ trợ emoji tốt)
    try:
        # Thử sử dụng font hệ thống
        font_large = ImageFont.truetype("arial.ttf", 60)
        font_medium = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        # Fallback font
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Vẽ icon
    draw.text((width//2, 80), icon, fill="#FFFFFF", font=font_large, anchor="mm")
    
    # Vẽ tiêu đề sách
    title_lines = []
    words = title.split()
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font_medium)
        if bbox[2] - bbox[0] < width - 40:
            current_line = test_line
        else:
            if current_line:
                title_lines.append(current_line)
            current_line = word
    
    if current_line:
        title_lines.append(current_line)
    
    # Giới hạn số dòng
    title_lines = title_lines[:3]
    
    # Vẽ từng dòng tiêu đề
    start_y = 180
    for i, line in enumerate(title_lines):
        y_pos = start_y + i * 30
        draw.text((width//2, y_pos), line, fill="#FFFFFF", font=font_medium, anchor="mm")
    
    # Vẽ thể loại
    draw.text((width//2, height - 60), genre, fill="#FFFFFF", font=font_small, anchor="mm")
    
    # Vẽ mã sách
    draw.text((width//2, height - 30), f"#{book_id:04d}", fill="#FFFFFF", font=font_small, anchor="mm")
    
    # Lưu file
    filename = f"book_{book_id:04d}_{genre.replace(' ', '_')}.jpg"
    filepath = os.path.join(UPLOADS_DIR, filename)
    image.save(filepath, "JPEG", quality=90)
    
    return f"/static/uploads/{filename}"

def update_book_covers():
    """Cập nhật hình ảnh bìa sách"""
    
    try:
        ensure_uploads_dir()
        db = get_db_connection()
        
        # Lấy tất cả sách từ database
        cursor = db.execute("SELECT id, title, genre, cover_url FROM books")
        books = cursor.fetchall()
        
        updated_count = 0
        
        for book_id, title, genre, current_cover in books:
            # Bỏ qua nếu đã có hình ảnh tùy chỉnh
            if current_cover and current_cover != "/static/placeholder.jpg" and "uploads" in current_cover:
                print(f"⏭️ Bỏ qua (đã có hình): {title}")
                continue
                
            print(f"🎨 Tạo hình ảnh cho: {title} ({genre})")
            
            try:
                # Tạo hình ảnh bìa sách
                new_cover_url = create_book_cover(title, genre, book_id)
                
                # Cập nhật database
                db.execute("UPDATE books SET cover_url = ? WHERE id = ?", (new_cover_url, book_id))
                updated_count += 1
                print(f"✅ Đã tạo: {title}")
                
            except Exception as e:
                print(f"❌ Lỗi tạo hình cho {title}: {e}")
                # Sử dụng placeholder mặc định
                db.execute("UPDATE books SET cover_url = ? WHERE id = ?", ("/static/placeholder.jpg", book_id))
        
        db.commit()
        print(f"\n🎉 Hoàn thành! Đã tạo {updated_count} hình ảnh bìa sách.")
        
        # Thống kê
        cursor = db.execute("SELECT COUNT(*) FROM books WHERE cover_url LIKE '/static/uploads/%'")
        books_with_covers = cursor.fetchone()[0]
        cursor = db.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]
        
        print(f"📊 Thống kê:")
        print(f"   - Tổng số sách: {total_books}")
        print(f"   - Sách có hình ảnh tùy chỉnh: {books_with_covers}")
        print(f"   - Sách dùng placeholder: {total_books - books_with_covers}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("🚀 Bắt đầu tạo hình ảnh bìa sách...")
    update_book_covers()
    print("✨ Hoàn thành!")

