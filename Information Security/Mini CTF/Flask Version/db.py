import sqlite3
import os
from werkzeug.security import generate_password_hash
from flags import FLAGS

DB_PATH = os.path.join(os.path.dirname(__file__), 'ctf.db')

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
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

        ('bac',     'Secret Admin Panel',  'Broken Access Control','Easy',   100,
         'A hidden admin endpoint exists but access control is only enforced on the frontend. The backend route only checks login, not role. Navigate directly to it as a regular player.',
         'Try navigating directly to /challenges/bac/secret-panel — the server never checks if you are actually an admin.',
         30, FLAGS['bac']),

        ('crypto',  'Encoded Message',     'Cryptography',         'Hard',   300,
         'An intercepted transmission contains an encoded message. Intelligence suggests it uses a classical substitution cipher with a shift of 13. Decode it to recover the flag.',
         'ROT13 is Caesar cipher with shift=13. Each letter shifts 13 positions forward in the alphabet. Numbers and symbols are unchanged.',
         50, FLAGS['crypto']),

        ('hash',    'Hash Cracking',       'Cryptography',         'Medium', 200,
         'A database breach has leaked password hashes. The admin password hash is: 5f4dcc3b5aa765d61d8327deb882cf99. Identify the hash algorithm, crack it using your knowledge of common passwords, and enter the plaintext to retrieve the flag.',
         'MD5 produces exactly 32 hexadecimal characters. This hash corresponds to one of the most common passwords ever used. Think: what would a lazy admin set as their password?',
         40, FLAGS['hash']),

        ('rsa',     'RSA Decryption',      'Cryptography',         'Hard',   300,
         'An RSA encrypted message has been intercepted. You are given: p = 61, q = 53, e = 17, Ciphertext = 2557. Use RSA mathematics to compute the private key d and decrypt the message. Steps: (1) n = p × q, (2) φ(n) = (p−1)(q−1), (3) find d where e×d ≡ 1 mod φ(n), (4) plaintext = ciphertext^d mod n.',
         'n = 3233, φ(n) = 3120, use extended Euclidean algorithm to find d. In Python: pow(ciphertext, d, n). The answer is a 2-digit number.',
         50, FLAGS['rsa']),

        ('bruteforce', 'Brute Force Login', 'Authentication',       'Medium', 200,
         'A login portal has no rate limiting, no account lockout, and no CAPTCHA. The admin used a password from the 10 most common passwords list. Try each one until you get in. Wordlist: password, 123456, admin, letmein, qwerty, monkey, dragon, master, abc123, password123',
         'Think about which password an overconfident sysadmin who thinks they are clever would choose. It means allow me to enter.',
         40, FLAGS['bruteforce']),

        ('diffie',  'Diffie-Hellman Exchange', 'Cryptography',      'Hard',   300,
         'Two parties are establishing a shared secret over an insecure channel using Diffie-Hellman key exchange. You have intercepted the public values. Given: Prime p = 23, Generator g = 5, Alice public key A = 8, Bob public key B = 19, Alice private key a = 6. Compute the shared secret that both Alice and Bob independently arrive at.',
         'Shared secret = B^a mod p. Bob computes it as A^b mod p — both give the same result. This is the magic of Diffie-Hellman.',
         50, FLAGS['diffie']),

        ('vigenere', 'Vigenere Cipher',    'Cryptography',         'Medium', 200,
         'A secret message has been encrypted using the Vigenere cipher — a polyalphabetic substitution cipher that uses a keyword to shift each letter by a different amount. Ciphertext: RIJVS{j4g3u3t3_m4ynh3t_nh4mz3x} Key: CRYPTO. Decrypt it to recover the flag.',
         'For each letter: plaintext = (ciphertext_letter - key_letter) mod 26. Numbers and symbols and the flag{} wrapper are NOT encrypted — only alphabetic characters inside are shifted. Apply the key cyclically.',
         40, FLAGS['vigenere']),
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
