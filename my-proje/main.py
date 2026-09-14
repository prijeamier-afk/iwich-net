import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

PORT = int(os.environ.get("PORT", 8080))
BASE_DIR = os.path.dirname(os.path.abspath(file))
DB_FILE = os.path.join(BASE_DIR, "users.db")

# ساخت جدول دیتابیس کاربران
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            uuid TEXT NOT NULL UNIQUE,
            data_limit_gb REAL,
            used_data_gb REAL DEFAULT 0,
            expiry_date TEXT,
            status TEXT DEFAULT 'active'
        )
    ''')
    conn.commit()
    conn.close()

class PanelHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            file_path = os.path.join(BASE_DIR, 'index.html')
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        elif self.path.startswith('/sub'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            file_path = os.path.join(BASE_DIR, 'sub.html')
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/api/users':
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT id, name, uuid, used_data_gb, data_limit_gb, expiry_date, status FROM users')
            rows = c.fetchall()
            conn.close()

            users_list = []
            for r in rows:
                users_list.append({
                    "id": r[0], "name": r[1], "uuid": r[2],
                    "used": r[3], "total": r[4], "expiry": r[5], "status": r[6]
                })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(users_list).encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/users/add':
            length = int(self.headers['Content-Length'])
            body = json.loads(self.rfile.read(length))

            name = body.get('name', 'User')
            user_uuid = body.get('uuid') or str(uuid.uuid4())
            limit_gb = float(body.get('limit', 30))
            days = int(body.get('days', 30))
            expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('INSERT INTO users (name, uuid, data_limit_gb, expiry_date) VALUES (?, ?, ?, ?)',
                      (name, user_uuid, limit_gb, expiry))
            conn.commit()
            conn.close()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))

if name == 'main':
    init_db()
    print(f"Iwich Panel is running on port {PORT}...")
    server = HTTPServer(('0.0.0.0', PORT), PanelHandler)
    server.serve_forever()