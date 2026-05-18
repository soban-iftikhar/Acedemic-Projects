# MiniCTF Platform
### InfoSec Lab Project — Educational CTF Challenge Platform

This project contains **two complete implementations** of the Mini CTF platform:

1. **Flask Version** - Python backend with Jinja2 templates & SQLite
2. **MERN Version** - Node.js/React full-stack with MongoDB

---

## 📁 Choose Your Version

### 🐍 Flask Version (Python)
```bash
cd "Flask Version"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
**Access:** http://localhost:5000

### 🔧 MERN Version (JavaScript)

**Backend:**
```bash
cd "MERN Version/backend"
npm install
npm run dev
```

**Frontend (new terminal):**
```bash
cd "MERN Version/frontend"
npm install
npm run dev
```
**Access:** http://localhost:5173

---

## Default Credentials

| Role   | Username | Password    |
|--------|----------|-------------|
| Admin  | admin    | Admin@1337  |
| Player | player1  | player123   |

---

## 7 Challenges

| # | Title              | Vulnerability          | Points |
|---|--------------------|------------------------|--------|
| 1 | Login Bypass       | SQL Injection          | 100    |
| 2 | Profile Viewer     | IDOR                   | 100    |
| 3 | Message Board      | Stored XSS             | 200    |
| 4 | Ping Utility       | Command Injection      | 200    |
| 5 | Avatar Upload      | Insecure File Upload   | 300    |
| 6 | Secret Admin Panel | Broken Access Control  | 100    |
| 7 | Encoded Message    | Cryptography (ROT13)   | 300    |

**Total: 1300 points**

---

## Challenge Solutions (for demo/grading)

### 1. SQL Injection
- Username: `' OR '1'='1`  
- Password: anything

### 2. IDOR
- Go to `/challenges/idor/profile?id=1`
- Admin's profile contains the flag

### 3. XSS
- Post: `<script>alert(document.cookie)</script>`
- The `ctf_flag` cookie contains the flag

### 4. Command Injection
- Input: `127.0.0.1; cat flag.txt`
- Flag is in `challenge_data/cmdi/flag.txt`

### 5. File Upload
- Create a file named `shell.py.png` with content: `f=open('secret_flag.txt');print(f.read())`
- Upload it — server executes and returns the flag

### 6. Broken Access Control
- Navigate directly to: `/challenges/bac/secret-panel`
- No admin check on the backend

### 7. Cryptography
- Encoded: `synt{p4rf4e_p1cu3e_e0g13_pe4px3q}`
- Apply ROT13 to decode
- Decoded flag: `flag{c4es4r_c1ph3r_r0t13_cr4ck3d}`

---

## Project Structure

```
mini_ctf/
├── app.py              # Main Flask app — all routes
├── db.py               # Database layer (SQLite)
├── auth.py             # Auth decorators & helpers
├── flags.py            # All flags & encoded values
├── requirements.txt
├── README.md
├── ctf.db              # Auto-created on first run
├── challenge_data/
│   ├── cmdi/
│   │   └── flag.txt    # Auto-created
│   └── upload/
│       └── secret_flag.txt  # Auto-created
└── templates/
    ├── base.html
    ├── auth/
    │   ├── login.html
    │   └── register.html
    ├── player/
    │   ├── dashboard.html
    │   ├── challenges.html
    │   ├── challenge_detail.html
    │   └── scoreboard.html
    ├── admin/
    │   ├── dashboard.html
    │   ├── users.html
    │   ├── challenges.html
    │   ├── challenge_form.html
    │   ├── submissions.html
    │   └── logs.html
    └── challenges/
        ├── sqli.html
        ├── idor.html
        ├── xss.html
        ├── cmdi.html
        ├── upload.html
        ├── bac.html
        └── crypto.html
```

---

## Tech Stack
- **Backend:** Python + Flask
- **Database:** SQLite (stdlib sqlite3)
- **Frontend:** Bootstrap 5 + Jinja2 + custom CSS
- **No external dependencies** beyond Flask

---

> ⚠️ **WARNING:** This app contains intentional vulnerabilities for educational purposes.
> Do NOT deploy on a public server.
