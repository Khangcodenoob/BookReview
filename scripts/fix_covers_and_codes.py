import os
import sqlite3
import time
import requests
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'books.db')
UPLOADS_DIR = os.path.join(BASE_DIR, 'static', 'uploads')

ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "gif", "webp"}

os.makedirs(UPLOADS_DIR, exist_ok=True)

if not os.path.exists(DB_PATH):
    print('Database not found at', DB_PATH)
    raise SystemExit(1)

bak = DB_PATH + f'.bak.{int(time.time())}'
print('Backing up DB to', bak)
import shutil
shutil.copy2(DB_PATH, bak)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

rows = cur.execute("SELECT id, title, cover_url, book_code FROM books ORDER BY id").fetchall()
updated_covers = 0
updated_codes = 0
for r in rows:
    bid = r['id']
    title = r['title']
    cover = r['cover_url'] or ''
    code = r['book_code'] or ''
    # fix cover
    if cover.startswith('http://') or cover.startswith('https://'):
        try:
            print(f'Downloading cover for {bid} - {title}: {cover}')
            resp = requests.get(cover, timeout=10)
            if resp.status_code == 200 and resp.content:
                parsed = urlparse(cover)
                name = os.path.basename(parsed.path) or f'cover_{bid}_{int(time.time())}.jpg'
                safe = secure_filename(name)
                ext = safe.rsplit('.', 1)[-1].lower() if '.' in safe else 'jpg'
                if ext not in ALLOWED_IMAGE_EXT:
                    ext = 'jpg'
                    safe = f"{safe}.{ext}" if '.' not in safe else safe
                dest_name = safe
                dest_path = os.path.join(UPLOADS_DIR, dest_name)
                base, dot, ex = dest_name.rpartition('.')
                i = 1
                while os.path.exists(dest_path):
                    dest_name = f"{base}_{i}.{ex}"
                    dest_path = os.path.join(UPLOADS_DIR, dest_name)
                    i += 1
                with open(dest_path, 'wb') as f:
                    f.write(resp.content)
                local = '/static/uploads/' + dest_name
                cur.execute('UPDATE books SET cover_url=? WHERE id=?', (local, bid))
                conn.commit()
                updated_covers += 1
                print('Saved ->', local)
            else:
                print('Failed to download, status', resp.status_code)
        except Exception as e:
            print('Error downloading', e)
    # fix code
    if not code:
        new_code = f"BK{bid:04d}"
        exists = cur.execute('SELECT 1 FROM books WHERE book_code=?', (new_code,)).fetchone()
        if exists:
            new_code = f"BK{bid}_{int(time.time())}"
        cur.execute('UPDATE books SET book_code=? WHERE id=?', (new_code, bid))
        conn.commit()
        updated_codes += 1
        print(f'Updated book_code for id {bid} -> {new_code}')

print('Done. covers updated:', updated_covers, 'codes updated:', updated_codes)
conn.close()
