from functools import wraps
from flask import session, redirect, url_for, flash
from db import get_db

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'error')
            return redirect(url_for('auth_login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'error')
            return redirect(url_for('auth_login'))
        if session.get('role') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('player_dashboard'))
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    if 'user_id' not in session:
        return None
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    db.close()
    return user

def log_activity(user_id, action, payload=None, ip=None):
    db = get_db()
    db.execute("INSERT INTO activity_logs (user_id, action, payload, ip_address) VALUES (?,?,?,?)",
               (user_id, action, payload, ip))
    db.commit()
    db.close()
