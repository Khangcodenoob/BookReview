import os
import sqlite3
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'books.db')
print('DB:', DB_PATH)
if not os.path.exists(DB_PATH):
    print('Database not found')
    raise SystemExit(1)
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT id, title, cover_url FROM books ORDER BY id")
rows = cur.fetchall()
print(f'Found {len(rows)} books')
for r in rows:
    cid = r['id']
    title = r['title']
    cover = r['cover_url'] or ''
    exists = 'N/A'
    local_path = ''
    if cover.startswith('/') or 'static' in cover:
        # try to map to workspace path
        local_rel = cover.lstrip('/')
        local_path = os.path.join(BASE_DIR, local_rel.replace('/', os.sep))
        exists = os.path.exists(local_path)
    print(f"{cid}\t{title}\t{cover}\tlocal_exists={exists}\t{local_path}")
conn.close()
