import sqlite3

# Cập nhật hình ảnh bìa sách thực tế
real_covers = {
    "Những người khốn khổ": "https://covers.openlibrary.org/b/isbn/9780140444308-L.jpg",
    "Chiến tranh và Hòa bình": "https://covers.openlibrary.org/b/isbn/9780140447934-L.jpg", 
    "Bố già": "https://covers.openlibrary.org/b/isbn/9780451205766-L.jpg",
    "1984": "https://covers.openlibrary.org/b/isbn/9780451524935-L.jpg",
    "Chúa tể những chiếc nhẫn": "https://covers.openlibrary.org/b/isbn/9780544003415-L.jpg",
    "Nghĩ giàu và làm giàu": "https://covers.openlibrary.org/b/isbn/9781585424337-L.jpg",
    "Tư duy nhanh và chậm": "https://covers.openlibrary.org/b/isbn/9780374533557-L.jpg",
    "Freakonomics": "https://covers.openlibrary.org/b/isbn/9780060731328-L.jpg",
    "Rich Dad Poor Dad": "https://covers.openlibrary.org/b/isbn/9781612680019-L.jpg",
    "The Lean Startup": "https://covers.openlibrary.org/b/isbn/9780307887894-L.jpg",
    "Lược sử thời gian": "https://covers.openlibrary.org/b/isbn/9780553380163-L.jpg",
    "Sapiens": "https://covers.openlibrary.org/b/isbn/9780062316097-L.jpg",
    "Cosmos": "https://covers.openlibrary.org/b/isbn/9780345539434-L.jpg",
    "The Selfish Gene": "https://covers.openlibrary.org/b/isbn/9780192860927-L.jpg",
    "A Brief History of Time": "https://covers.openlibrary.org/b/isbn/9780553380163-L.jpg",
    "Tư duy tích cực": "https://covers.openlibrary.org/b/isbn/9780743234801-L.jpg",
    "Emotional Intelligence": "https://covers.openlibrary.org/b/isbn/9780553804916-L.jpg",
    "The Power of Now": "https://covers.openlibrary.org/b/isbn/9781577314806-L.jpg",
    "Man's Search for Meaning": "https://covers.openlibrary.org/b/isbn/9780807014295-L.jpg",
    "Thinking, Fast and Slow": "https://covers.openlibrary.org/b/isbn/9780374533557-L.jpg",
    "Truyện Kiều": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop",
    "Nhật ký trong tù": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop",
    "Dế Mèn phiêu lưu ký": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop",
    "Số đỏ": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop",
    "Chí Phèo": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop",
    "Lịch sử Việt Nam": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop",
    "The Art of War": "https://covers.openlibrary.org/b/isbn/9781590309637-L.jpg",
    "Guns, Germs, and Steel": "https://covers.openlibrary.org/b/isbn/9780393317558-L.jpg",
    "The Rise and Fall of the Third Reich": "https://covers.openlibrary.org/b/isbn/9781451651683-L.jpg",
    "A People's History of the United States": "https://covers.openlibrary.org/b/isbn/9780062397348-L.jpg",
    "Harry Potter và Hòn đá Phù thủy": "https://covers.openlibrary.org/b/isbn/9780439708180-L.jpg",
    "Alice ở xứ sở thần tiên": "https://covers.openlibrary.org/b/isbn/9780141439761-L.jpg",
    "Peter Pan": "https://covers.openlibrary.org/b/isbn/9780141322575-L.jpg",
    "The Little Prince": "https://covers.openlibrary.org/b/isbn/9780156012195-L.jpg",
    "Winnie-the-Pooh": "https://covers.openlibrary.org/b/isbn/9780525444435-L.jpg",
}

try:
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    
    updated = 0
    for title, cover_url in real_covers.items():
        cursor.execute("UPDATE books SET cover_url = ? WHERE title = ?", (cover_url, title))
        if cursor.rowcount > 0:
            updated += 1
            print(f"Updated: {title}")
    
    conn.commit()
    conn.close()
    
    print(f"Updated {updated} book covers!")
    
except Exception as e:
    print(f"Error: {e}")
