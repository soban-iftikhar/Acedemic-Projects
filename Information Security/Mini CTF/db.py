import sqlite3
import os
from werkzeug.security import generate_password_hash
from flags import FLAGS

DB_PATH = os.path.join(os.path.dirname(__file__), 'ctf.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'player',
            score INTEGER DEFAULT 0,
            secret_data TEXT DEFAULT 'Nothing here.',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            points INTEGER NOT NULL,
            description TEXT NOT NULL,
            hint TEXT,
            hint_cost INTEGER DEFAULT 30,
            flag TEXT NOT NULL,
            active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            challenge_id INTEGER NOT NULL,
            submitted_flag TEXT NOT NULL,
            correct INTEGER DEFAULT 0,
            first_blood INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(challenge_id) REFERENCES challenges(id)
        );

        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            payload TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS xss_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS vuln_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        );
    ''')

    # Seed admin user
    existing = c.execute("SELECT id FROM users WHERE username='admin'").fetchone()
    if not existing:
        c.execute("INSERT INTO users (username, email, password, role, score, secret_data) VALUES (?,?,?,?,?,?)",
                  ('admin', 'admin@ctf.local', generate_password_hash('Admin@1337'),
                   'admin', 0, 'flag_holder: ' + FLAGS['idor']))
        c.execute("INSERT INTO users (username, email, password, role, score, secret_data) VALUES (?,?,?,?,?,?)",
                  ('player1', 'player1@ctf.local', generate_password_hash('player123'),
                   'player', 0, 'Nothing interesting here.'))

    # Seed vuln_users for SQLi challenge
    vuln_count = c.execute("SELECT COUNT(*) FROM vuln_users").fetchone()[0]
    if vuln_count == 0:
        c.execute("INSERT INTO vuln_users (username, password, role) VALUES ('admin','S3cr3tP4ss!','admin')")
        c.execute("INSERT INTO vuln_users (username, password, role) VALUES ('alice','alice123','user')")

    # Seed challenges
    challenges = [
        ('sqli',    'Login Bypass',        'Injection',            'Easy',   100,
         'A legacy login portal was deployed without proper input sanitization. The developer trusted user input directly inside SQL queries. Can you bypass authentication without knowing the password?',
         'Think about how SQL queries are constructed. What happens if you close a string early with a quote character?',
         30, FLAGS['sqli']),

        ('idor',    'Profile Viewer',      'Broken Access Control','Easy',   100,
         "A social platform exposes user profiles via a predictable ID parameter in the URL. There are no server-side checks to verify ownership. Find the admin's hidden profile data.",
         'User IDs are sequential integers. The admin account was created first — try ID 1.',
         30, FLAGS['idor']),

        ('xss',     'Message Board',       'XSS',                  'Medium', 200,
         'A public message board renders user input directly into the HTML without any sanitization. The flag is stored in a cookie. Inject a script to read document.cookie.',
         "Try a basic script tag. The flag is stored in the page cookie named ctf_flag. Use document.cookie to access it.",
         40, FLAGS['xss']),

        ('cmdi',    'Ping Utility',        'Command Injection',    'Medium', 200,
         'An internal network tool lets admins ping any host. The input is passed directly to the OS shell. Break out of the ping command and read the flag file.',
         'Shell separators like ; && || let you chain commands. The flag is in flag.txt in the challenge directory.',
         40, FLAGS['cmdi']),

        ('upload',  'Avatar Upload',       'File Upload',          'Hard',   300,
         'A profile picture upload feature only checks the file extension string — not actual file content. Upload a Python script disguised as an image to read the server-side flag.',
         'The server checks os.path.splitext(filename). Try a double extension like shell.py.png and upload a Python script that reads secret_flag.txt.',
         50, FLAGS['upload']),

        ('bac',     'Secret Admin Panel',  'Broken Access Control','Easy',   100,
         'A hidden admin endpoint exists but access control is only enforced on the frontend. The backend route only checks login, not role. Navigate directly to it as a regular player.',
         'Try navigating directly to /challenges/bac/secret-panel — the server never checks if you are actually an admin.',
         30, FLAGS['bac']),

        ('crypto',  'Encoded Message',     'Cryptography',         'Hard',   300,
         'An intercepted transmission contains an encoded message. Intelligence suggests it uses a classical substitution cipher with a shift of 13. Decode it to recover the flag.',
         'ROT13 is Caesar cipher with shift=13. Each letter shifts 13 positions forward in the alphabet. Numbers and symbols are unchanged.',
         50, FLAGS['crypto']),
    ]

    for ch in challenges:
        exists = c.execute("SELECT id FROM challenges WHERE slug=?", (ch[0],)).fetchone()
        if not exists:
            c.execute('''INSERT INTO challenges
                         (slug,title,category,difficulty,points,description,hint,hint_cost,flag)
                         VALUES (?,?,?,?,?,?,?,?,?)''', ch)

    conn.commit()
    conn.close()
    print("[+] Database initialized successfully.")

if __name__ == '__main__':
    init_db()
