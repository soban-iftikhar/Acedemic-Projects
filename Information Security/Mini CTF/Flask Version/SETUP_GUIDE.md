# Flask Version - Mini CTF Setup Guide

## 📋 Prerequisites
- Python 3.8+
- pip (Python package manager)
- SQLite (included with Python)

## 🚀 Installation

### 1. Create Virtual Environment
```bash
cd "Flask Version"
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
python app.py
```

The application will:
- Automatically create `ctf.db` SQLite database
- Initialize default admin and player accounts
- Create challenge data files
- Start server at `http://localhost:5000`

## 👤 Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | Admin@1337 |
| Player | player1 | player123 |

## 📖 First Steps

1. **Admin Access:**
   - Login with `admin` credentials
   - Visit `/admin/dashboard` to manage challenges
   - View logs, submissions, and users

2. **Player Mode:**
   - Login with `player1` credentials
   - Solve challenges from `/challenges`
   - Check leaderboard at `/scoreboard`

## 🎯 Challenge List

1. **SQL Injection** (100 pts) - Easy
2. **IDOR** (100 pts) - Easy  
3. **XSS** (200 pts) - Medium
4. **Command Injection** (200 pts) - Medium
5. **File Upload** (300 pts) - Hard
6. **Broken Access Control** (100 pts) - Easy
7. **Cryptography** (300 pts) - Hard

## 🔍 File Structure
```
Flask Version/
├── app.py              # Main Flask application
├── auth.py             # Authentication decorators
├── db.py               # Database setup
├── flags.py            # Challenge flags
├── requirements.txt    # Dependencies
├── ctf.db             # SQLite database (auto-created)
├── templates/         # HTML templates
├── static/            # CSS & JavaScript
└── challenge_data/    # Challenge files
```

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Change port in app.py
app.run(debug=True, port=5001)
```

### Database Reset
```bash
rm ctf.db
python app.py
```

### Virtual Environment Issues
```bash
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📝 Notes
- This is an educational platform for learning security vulnerabilities
- All vulnerabilities are intentional for learning purposes
- Never use this as a template for production code
- SQLite database is stored locally (no backup)

---
**Last Updated:** May 18, 2026
