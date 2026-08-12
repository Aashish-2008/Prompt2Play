import sqlite3
import time
from werkzeug.security import generate_password_hash, check_password_hash

SCHEMA = '''
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT,
  password_hash TEXT NOT NULL,
  created_at INTEGER
);

CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  prompt TEXT,
  title TEXT,
  genre TEXT,
  filename TEXT,
  created_at INTEGER,
  FOREIGN KEY(user_id) REFERENCES users(id)
);
'''


def get_conn(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str):
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    conn.commit()
    conn.close()


def create_user(db_path: str, username: str, email: str, password: str):
    pw_hash = generate_password_hash(password)
    now = int(time.time())
    conn = get_conn(db_path)
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO users (username,email,password_hash,created_at) VALUES (?,?,?,?)', (username,email,pw_hash,now))
        conn.commit()
        uid = cur.lastrowid
        return uid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def authenticate_user(db_path: str, username: str, password: str):
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, username))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    if check_password_hash(row['password_hash'], password):
        return {'id': row['id'], 'username': row['username'], 'email': row['email']}
    return None


def get_user_by_id(db_path: str, uid: int):
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute('SELECT id, username, email, created_at FROM users WHERE id = ?', (uid,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def save_project(db_path: str, user_id: int, prompt: str, title: str, genre: str, filename: str):
    now = int(time.time())
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute('INSERT INTO projects (user_id,prompt,title,genre,filename,created_at) VALUES (?,?,?,?,?,?)', (user_id,prompt,title,genre,filename,now))
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid


def get_projects_by_user(db_path: str, user_id: int):
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute('SELECT id,prompt,title,genre,filename,created_at FROM projects WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
