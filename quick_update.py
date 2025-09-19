import sqlite3

conn = sqlite3.connect('books.db')
cursor = conn.cursor()

# Cập nhật một số sách quan trọng
updates = [
    ("Những người khốn khổ", "https://covers.openlibrary.org/b/isbn/9780140444308-L.jpg"),
    ("1984", "https://covers.openlibrary.org/b/isbn/9780451524935-L.jpg"),
    ("Harry Potter và Hòn đá Phù thủy", "https://covers.openlibrary.org/b/isbn/9780439708180-L.jpg"),
    ("The Little Prince", "https://covers.openlibrary.org/b/isbn/9780156012195-L.jpg"),
    ("Sapiens", "https://covers.openlibrary.org/b/isbn/9780062316097-L.jpg"),
]

for title, url in updates:
    cursor.execute("UPDATE books SET cover_url = ? WHERE title = ?", (url, title))
    print(f"Updated: {title}")

conn.commit()
conn.close()
print("Done!")
