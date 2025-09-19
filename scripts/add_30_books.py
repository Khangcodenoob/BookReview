#!/usr/bin/env python3
"""
Script để thêm 30 sách mới vào database
"""

import os
import sqlite3
import time
from typing import List, Tuple

# Đường dẫn database
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "books.db")

def get_db_connection():
    """Tạo kết nối database"""
    return sqlite3.connect(DB_PATH)

def ensure_categories_exist(db: sqlite3.Connection):
    """Đảm bảo các danh mục tồn tại"""
    categories = [
        'Tiểu thuyết', 'Truyện ngắn', 'Kinh tế', 'Văn học', 
        'Khoa học', 'Tâm lý', 'Thiếu nhi', 'Lịch sử', 'Khác'
    ]
    
    for category in categories:
        db.execute("INSERT OR IGNORE INTO categories (name, slug) VALUES (?, ?)", (category, None))
    db.commit()

def get_category_id(db: sqlite3.Connection, category_name: str) -> int:
    """Lấy ID của danh mục"""
    result = db.execute("SELECT id FROM categories WHERE name = ?", (category_name,)).fetchone()
    return result[0] if result else None

def add_books_to_database():
    """Thêm 30 sách mới vào database"""
    
    # Danh sách 30 sách với đầy đủ thông tin
    books_data = [
        # Tiểu thuyết
        ("Những người khốn khổ", "Victor Hugo", "/static/placeholder.jpg", 
         "Tác phẩm kinh điển của văn học Pháp, kể về cuộc đời của Jean Valjean và những người xung quanh trong bối cảnh nước Pháp thế kỷ 19.", 
         "Tiểu thuyết", "NXB Văn học", 1200, "TT001"),
        
        ("Chiến tranh và Hòa bình", "Leo Tolstoy", "/static/placeholder.jpg",
         "Bộ tiểu thuyết sử thi vĩ đại của văn học Nga, mô tả cuộc sống của giới quý tộc Nga trong thời kỳ Napoleon.",
         "Tiểu thuyết", "NXB Văn học", 1500, "TT002"),
        
        ("Bố già", "Mario Puzo", "/static/placeholder.jpg",
         "Câu chuyện về gia đình mafia Corleone và Don Vito Corleone, một trong những tiểu thuyết tội phạm nổi tiếng nhất.",
         "Tiểu thuyết", "NXB Trẻ", 450, "TT003"),
        
        ("1984", "George Orwell", "/static/placeholder.jpg",
         "Tác phẩm dystopian kinh điển về một xã hội toàn trị, nơi tự do cá nhân bị kiểm soát hoàn toàn.",
         "Tiểu thuyết", "NXB Hội nhà văn", 320, "TT004"),
        
        ("Chúa tể những chiếc nhẫn", "J.R.R. Tolkien", "/static/placeholder.jpg",
         "Bộ tiểu thuyết fantasy huyền thoại về cuộc phiêu lưu của Frodo Baggins để tiêu diệt chiếc nhẫn quyền lực.",
         "Tiểu thuyết", "NXB Trẻ", 1200, "TT005"),
        
        # Kinh tế
        ("Nghĩ giàu và làm giàu", "Napoleon Hill", "/static/placeholder.jpg",
         "Cuốn sách kinh điển về tư duy làm giàu, chia sẻ 13 nguyên tắc thành công từ những người giàu có nhất thế giới.",
         "Kinh tế", "NXB Lao động", 280, "KT001"),
        
        ("Tư duy nhanh và chậm", "Daniel Kahneman", "/static/placeholder.jpg",
         "Khám phá hai hệ thống tư duy của con người và cách chúng ảnh hưởng đến quyết định trong cuộc sống và kinh doanh.",
         "Kinh tế", "NXB Thế giới", 450, "KT002"),
        
        ("Freakonomics", "Steven D. Levitt & Stephen J. Dubner", "/static/placeholder.jpg",
         "Áp dụng kinh tế học vào những vấn đề bất ngờ trong cuộc sống, từ tội phạm đến giáo dục.",
         "Kinh tế", "NXB Trẻ", 320, "KT003"),
        
        ("Rich Dad Poor Dad", "Robert Kiyosaki", "/static/placeholder.jpg",
         "So sánh tư duy tài chính giữa hai người cha và cách tư duy đúng đắn về tiền bạc.",
         "Kinh tế", "NXB Lao động", 250, "KT004"),
        
        ("The Lean Startup", "Eric Ries", "/static/placeholder.jpg",
         "Phương pháp khởi nghiệp tinh gọn, tập trung vào việc học hỏi nhanh và tối ưu hóa sản phẩm.",
         "Kinh tế", "NXB Thế giới", 300, "KT005"),
        
        # Khoa học
        ("Lược sử thời gian", "Stephen Hawking", "/static/placeholder.jpg",
         "Giải thích các khái niệm vật lý phức tạp về vũ trụ, thời gian và không gian một cách dễ hiểu.",
         "Khoa học", "NXB Trẻ", 280, "KH001"),
        
        ("Sapiens", "Yuval Noah Harari", "/static/placeholder.jpg",
         "Lược sử loài người từ thời tiền sử đến hiện tại, khám phá những bước ngoặt quan trọng trong lịch sử.",
         "Khoa học", "NXB Thế giới", 450, "KH002"),
        
        ("Cosmos", "Carl Sagan", "/static/placeholder.jpg",
         "Hành trình khám phá vũ trụ và khoa học, từ những hành tinh xa xôi đến sự sống trên Trái Đất.",
         "Khoa học", "NXB Trẻ", 400, "KH003"),
        
        ("The Selfish Gene", "Richard Dawkins", "/static/placeholder.jpg",
         "Giải thích thuyết tiến hóa từ góc độ gen, cách gen 'ích kỷ' định hình hành vi của các sinh vật.",
         "Khoa học", "NXB Thế giới", 350, "KH004"),
        
        ("A Brief History of Time", "Stephen Hawking", "/static/placeholder.jpg",
         "Khám phá những bí ẩn của vũ trụ, từ Big Bang đến lỗ đen, được viết bằng ngôn ngữ dễ hiểu.",
         "Khoa học", "NXB Trẻ", 250, "KH005"),
        
        # Tâm lý
        ("Tư duy tích cực", "Norman Vincent Peale", "/static/placeholder.jpg",
         "Phương pháp thay đổi tư duy để có cuộc sống tích cực và thành công hơn.",
         "Tâm lý", "NXB Lao động", 300, "TL001"),
        
        ("Emotional Intelligence", "Daniel Goleman", "/static/placeholder.jpg",
         "Khám phá tầm quan trọng của trí tuệ cảm xúc trong thành công cá nhân và nghề nghiệp.",
         "Tâm lý", "NXB Thế giới", 380, "TL002"),
        
        ("The Power of Now", "Eckhart Tolle", "/static/placeholder.jpg",
         "Hướng dẫn sống trong hiện tại và tìm thấy sự bình an nội tâm thông qua thiền định.",
         "Tâm lý", "NXB Trẻ", 250, "TL003"),
        
        ("Man's Search for Meaning", "Viktor E. Frankl", "/static/placeholder.jpg",
         "Câu chuyện về ý nghĩa cuộc sống từ trải nghiệm trong trại tập trung và triết lý logotherapy.",
         "Tâm lý", "NXB Hội nhà văn", 200, "TL004"),
        
        ("Thinking, Fast and Slow", "Daniel Kahneman", "/static/placeholder.jpg",
         "Khám phá hai hệ thống tư duy và cách chúng ảnh hưởng đến quyết định hàng ngày.",
         "Tâm lý", "NXB Thế giới", 450, "TL005"),
        
        # Văn học
        ("Truyện Kiều", "Nguyễn Du", "/static/placeholder.jpg",
         "Kiệt tác văn học Việt Nam, kể về cuộc đời đầy bi kịch của Thúy Kiều.",
         "Văn học", "NXB Văn học", 350, "VL001"),
        
        ("Nhật ký trong tù", "Hồ Chí Minh", "/static/placeholder.jpg",
         "Tập thơ được viết trong thời gian Bác bị giam cầm, thể hiện tinh thần lạc quan và yêu nước.",
         "Văn học", "NXB Văn học", 150, "VL002"),
        
        ("Dế Mèn phiêu lưu ký", "Tô Hoài", "/static/placeholder.jpg",
         "Câu chuyện phiêu lưu của chú dế mèn, một tác phẩm thiếu nhi kinh điển của Việt Nam.",
         "Văn học", "NXB Kim Đồng", 200, "VL003"),
        
        ("Số đỏ", "Vũ Trọng Phụng", "/static/placeholder.jpg",
         "Tiểu thuyết châm biếm xã hội Việt Nam đầu thế kỷ 20, phê phán lối sống đạo đức giả.",
         "Văn học", "NXB Văn học", 300, "VL004"),
        
        ("Chí Phèo", "Nam Cao", "/static/placeholder.jpg",
         "Truyện ngắn nổi tiếng về số phận bi kịch của người nông dân trong xã hội cũ.",
         "Văn học", "NXB Văn học", 100, "VL005"),
        
        # Lịch sử
        ("Lịch sử Việt Nam", "Trần Trọng Kim", "/static/placeholder.jpg",
         "Bộ sử Việt Nam từ thời cổ đại đến đầu thế kỷ 20, được viết một cách khách quan và chi tiết.",
         "Lịch sử", "NXB Văn học", 800, "LS001"),
        
        ("The Art of War", "Sun Tzu", "/static/placeholder.jpg",
         "Binh pháp cổ đại Trung Quốc, chứa đựng những nguyên tắc chiến lược vẫn còn giá trị đến ngày nay.",
         "Lịch sử", "NXB Thế giới", 200, "LS002"),
        
        ("Guns, Germs, and Steel", "Jared Diamond", "/static/placeholder.jpg",
         "Giải thích tại sao một số nền văn minh phát triển hơn những nền văn minh khác trong lịch sử.",
         "Lịch sử", "NXB Trẻ", 450, "LS003"),
        
        ("The Rise and Fall of the Third Reich", "William L. Shirer", "/static/placeholder.jpg",
         "Lịch sử chi tiết về sự trỗi dậy và sụp đổ của Đức Quốc xã trong Thế chiến II.",
         "Lịch sử", "NXB Thế giới", 1200, "LS004"),
        
        ("A People's History of the United States", "Howard Zinn", "/static/placeholder.jpg",
         "Lịch sử nước Mỹ từ góc nhìn của những người bình thường, thay vì các nhà lãnh đạo.",
         "Lịch sử", "NXB Trẻ", 600, "LS005"),
        
        # Thiếu nhi
        ("Harry Potter và Hòn đá Phù thủy", "J.K. Rowling", "/static/placeholder.jpg",
         "Câu chuyện về cậu bé phù thủy Harry Potter và cuộc phiêu lưu đầu tiên tại trường Hogwarts.",
         "Thiếu nhi", "NXB Trẻ", 300, "TN001"),
        
        ("Alice ở xứ sở thần tiên", "Lewis Carroll", "/static/placeholder.jpg",
         "Cuộc phiêu lưu kỳ diệu của cô bé Alice trong thế giới tưởng tượng đầy màu sắc.",
         "Thiếu nhi", "NXB Kim Đồng", 200, "TN002"),
        
        ("Peter Pan", "J.M. Barrie", "/static/placeholder.jpg",
         "Câu chuyện về cậu bé không bao giờ lớn và cuộc phiêu lưu ở Neverland.",
         "Thiếu nhi", "NXB Kim Đồng", 250, "TN003"),
        
        ("The Little Prince", "Antoine de Saint-Exupéry", "/static/placeholder.jpg",
         "Câu chuyện triết lý sâu sắc về tình bạn, tình yêu và ý nghĩa cuộc sống qua lời kể của hoàng tử nhỏ.",
         "Thiếu nhi", "NXB Kim Đồng", 100, "TN004"),
        
        ("Winnie-the-Pooh", "A.A. Milne", "/static/placeholder.jpg",
         "Những câu chuyện ngọt ngào về chú gấu Pooh và các bạn trong Rừng Trăm Mẫu.",
         "Thiếu nhi", "NXB Kim Đồng", 180, "TN005"),
    ]
    
    try:
        db = get_db_connection()
        
        # Đảm bảo các danh mục tồn tại
        ensure_categories_exist(db)
        
        # Thêm sách vào database
        for book_data in books_data:
            title, author, cover_url, description, genre, publisher, num_pages, book_code = book_data
            
            # Lấy category_id
            category_id = get_category_id(db, genre)
            
            # Thêm sách
            db.execute("""
                INSERT INTO books (title, author, cover_url, description, genre, publisher, num_pages, book_code, category_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, author, cover_url, description, genre, publisher, num_pages, book_code, category_id))
        
        db.commit()
        print(f"✅ Đã thêm thành công {len(books_data)} sách vào database!")
        
        # Hiển thị thống kê
        cursor = db.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]
        print(f"📚 Tổng số sách trong database: {total_books}")
        
        # Thống kê theo thể loại
        cursor = db.execute("SELECT genre, COUNT(*) FROM books GROUP BY genre ORDER BY COUNT(*) DESC")
        print("\n📊 Thống kê theo thể loại:")
        for genre, count in cursor.fetchall():
            print(f"   {genre}: {count} sách")
            
    except Exception as e:
        print(f"❌ Lỗi khi thêm sách: {e}")
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("🚀 Bắt đầu thêm 30 sách mới vào database...")
    add_books_to_database()
    print("✨ Hoàn thành!")
