import sqlite3
import os

# Get the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'books.db')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Update some important books
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
