import os
import subprocess
import sqlite3
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, make_response)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from db import get_db, init_db
from auth import login_required, admin_required, get_current_user, log_activity
from flags import FLAGS, CRYPTO_ENCODED

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'challenge_data', 'upload')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ── Helpers ────────────────────────────────────────────────────────────────────

def get_solved_ids(user_id):
    db = get_db()
    rows = db.execute(
        "SELECT challenge_id FROM submissions WHERE user_id=? AND correct=1", (user_id,)
    ).fetchall()
    db.close()
    return [r['challenge_id'] for r in rows]

# ── Auth Routes ────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('player_dashboard'))
    return redirect(url_for('auth_login'))

@app.route('/auth/login', methods=['GET', 'POST'])
def auth_login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        db.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            log_activity(user['id'], 'LOGIN_SUCCESS', ip=request.remote_addr)
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('player_dashboard'))
        log_activity(None, 'LOGIN_FAIL', payload=f'user={username}', ip=request.remote_addr)
        flash('Invalid credentials.', 'error')
    return render_template('auth/login.html')

@app.route('/auth/register', methods=['GET', 'POST'])
def auth_register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('auth/register.html')
        db = get_db()
        if db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone():
            flash('Username already taken.', 'error')
            db.close()
            return render_template('auth/register.html')
        if db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
            flash('Email already registered.', 'error')
            db.close()
            return render_template('auth/register.html')
        db.execute(
            "INSERT INTO users (username, email, password, role, score, secret_data) VALUES (?,?,?,?,?,?)",
            (username, email, generate_password_hash(password), 'player', 0, 'Nothing interesting here.')
        )
        db.commit()
        db.close()
        flash('Registration successful. You may now login.', 'success')
        return redirect(url_for('auth_login'))
    return render_template('auth/register.html')

@app.route('/auth/logout')
def auth_logout():
    session.clear()
    flash('Session terminated.', 'info')
    return redirect(url_for('auth_login'))

# ── Player Routes ──────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def player_dashboard():
    user = get_current_user()
    db = get_db()
    challenges = db.execute("SELECT * FROM challenges WHERE active=1").fetchall()
    db.close()
    solved_ids = get_solved_ids(user['id'])
    return render_template('player/dashboard.html',
                           user=user, challenges=challenges,
                           solved_ids=solved_ids, total=len(challenges))

@app.route('/challenges')
@login_required
def player_challenges():
    user = get_current_user()
    db = get_db()
    challenges = db.execute("SELECT * FROM challenges WHERE active=1").fetchall()
    db.close()
    solved_ids = get_solved_ids(user['id'])
    return render_template('player/challenges.html',
                           user=user, challenges=challenges, solved_ids=solved_ids)

@app.route('/challenge/<slug>')
@login_required
def challenge_detail(slug):
    user = get_current_user()
    db = get_db()
    ch = db.execute("SELECT * FROM challenges WHERE slug=? AND active=1", (slug,)).fetchone()
    db.close()
    if not ch:
        flash('Challenge not found.', 'error')
        return redirect(url_for('player_challenges'))
    solved_ids = get_solved_ids(user['id'])
    already_solved = ch['id'] in solved_ids
    return render_template('player/challenge_detail.html',
                           user=user, challenge=ch, already_solved=already_solved)

@app.route('/submit/<slug>', methods=['POST'])
@login_required
def submit_flag(slug):
    user = get_current_user()
    db = get_db()
    ch = db.execute("SELECT * FROM challenges WHERE slug=? AND active=1", (slug,)).fetchone()
    if not ch:
        db.close()
        return redirect(url_for('player_challenges'))

    solved_ids = get_solved_ids(user['id'])
    if ch['id'] in solved_ids:
        flash('Already solved!', 'info')
        db.close()
        return redirect(url_for('challenge_detail', slug=slug))

    submitted = request.form.get('flag', '').strip()
    correct = (submitted == ch['flag'])

    first_blood = False
    if correct:
        prior = db.execute(
            "SELECT id FROM submissions WHERE challenge_id=? AND correct=1", (ch['id'],)
        ).fetchone()
        first_blood = (prior is None)

    db.execute(
        "INSERT INTO submissions (user_id, challenge_id, submitted_flag, correct, first_blood) VALUES (?,?,?,?,?)",
        (user['id'], ch['id'], submitted, 1 if correct else 0, 1 if first_blood else 0)
    )
    log_activity(user['id'], 'FLAG_SUBMIT',
                 payload=f'challenge={slug} flag={submitted} correct={correct}',
                 ip=request.remote_addr)
    if correct:
        db.execute("UPDATE users SET score = score + ? WHERE id=?", (ch['points'], user['id']))
        db.commit()
        db.close()
        msg = f'Correct! +{ch["points"]} pts'
        if first_blood:
            msg += ' 🩸 First Blood!'
        flash(msg, 'success')
    else:
        db.commit()
        db.close()
        flash('Wrong flag. Keep trying.', 'error')
    return redirect(url_for('challenge_detail', slug=slug))

@app.route('/hint/<slug>', methods=['POST'])
@login_required
def use_hint(slug):
    user = get_current_user()
    db = get_db()
    ch = db.execute("SELECT * FROM challenges WHERE slug=? AND active=1", (slug,)).fetchone()
    if not ch:
        db.close()
        return redirect(url_for('player_challenges'))
    if user['score'] >= ch['hint_cost']:
        db.execute("UPDATE users SET score = score - ? WHERE id=?", (ch['hint_cost'], user['id']))
        db.commit()
        db.close()
        flash(f'Hint: {ch["hint"]} (–{ch["hint_cost"]} pts)', 'info')
    else:
        db.close()
        flash('Not enough points to buy a hint.', 'error')
    return redirect(url_for('challenge_detail', slug=slug))

@app.route('/scoreboard')
@login_required
def player_scoreboard():
    db = get_db()
    players = db.execute(
        "SELECT * FROM users WHERE role='player' ORDER BY score DESC"
    ).fetchall()
    solved_counts = {}
    for p in players:
        count = db.execute(
            "SELECT COUNT(*) as c FROM submissions WHERE user_id=? AND correct=1", (p['id'],)
        ).fetchone()['c']
        solved_counts[p['id']] = count
    db.close()
    user = get_current_user()
    return render_template('player/scoreboard.html',
                           user=user, players=players, solved_counts=solved_counts)

# ── Admin Routes ───────────────────────────────────────────────────────────────

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    db = get_db()
    total_users       = db.execute("SELECT COUNT(*) as c FROM users WHERE role='player'").fetchone()['c']
    total_challenges  = db.execute("SELECT COUNT(*) as c FROM challenges").fetchone()['c']
    total_subs        = db.execute("SELECT COUNT(*) as c FROM submissions").fetchone()['c']
    correct_subs      = db.execute("SELECT COUNT(*) as c FROM submissions WHERE correct=1").fetchone()['c']
    recent_logs       = db.execute(
        "SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT 20"
    ).fetchall()
    db.close()
    user = get_current_user()
    return render_template('admin/dashboard.html', user=user,
                           total_users=total_users, total_challenges=total_challenges,
                           total_subs=total_subs, correct_subs=correct_subs,
                           recent_logs=recent_logs)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    db = get_db()
    players = db.execute("SELECT * FROM users WHERE role='player' ORDER BY score DESC").fetchall()
    solved_counts = {}
    for p in players:
        c = db.execute("SELECT COUNT(*) as c FROM submissions WHERE user_id=? AND correct=1", (p['id'],)).fetchone()['c']
        solved_counts[p['id']] = c
    db.close()
    user = get_current_user()
    return render_template('admin/users.html', user=user, players=players, solved_counts=solved_counts)

@app.route('/admin/challenges')
@login_required
@admin_required
def admin_challenges():
    db = get_db()
    challenges = db.execute("SELECT * FROM challenges").fetchall()
    db.close()
    user = get_current_user()
    return render_template('admin/challenges.html', user=user, challenges=challenges)

@app.route('/admin/challenges/add', methods=['GET','POST'])
@login_required
@admin_required
def admin_add_challenge():
    if request.method == 'POST':
        db = get_db()
        db.execute('''INSERT INTO challenges (slug,title,category,difficulty,points,description,hint,flag)
                      VALUES (?,?,?,?,?,?,?,?)''',
                   (request.form['slug'], request.form['title'], request.form['category'],
                    request.form['difficulty'], int(request.form['points']),
                    request.form['description'], request.form.get('hint',''),
                    request.form['flag']))
        db.commit()
        db.close()
        flash('Challenge added.', 'success')
        return redirect(url_for('admin_challenges'))
    user = get_current_user()
    return render_template('admin/challenge_form.html', user=user, challenge=None)

@app.route('/admin/challenges/edit/<int:cid>', methods=['GET','POST'])
@login_required
@admin_required
def admin_edit_challenge(cid):
    db = get_db()
    ch = db.execute("SELECT * FROM challenges WHERE id=?", (cid,)).fetchone()
    if not ch:
        db.close()
        return redirect(url_for('admin_challenges'))
    if request.method == 'POST':
        active = 1 if 'active' in request.form else 0
        db.execute('''UPDATE challenges SET title=?,category=?,difficulty=?,points=?,
                      description=?,hint=?,flag=?,active=? WHERE id=?''',
                   (request.form['title'], request.form['category'], request.form['difficulty'],
                    int(request.form['points']), request.form['description'],
                    request.form.get('hint',''), request.form['flag'], active, cid))
        db.commit()
        db.close()
        flash('Challenge updated.', 'success')
        return redirect(url_for('admin_challenges'))
    db.close()
    user = get_current_user()
    return render_template('admin/challenge_form.html', user=user, challenge=ch)

@app.route('/admin/challenges/delete/<int:cid>', methods=['POST'])
@login_required
@admin_required
def admin_delete_challenge(cid):
    db = get_db()
    db.execute("DELETE FROM challenges WHERE id=?", (cid,))
    db.commit()
    db.close()
    flash('Challenge deleted.', 'success')
    return redirect(url_for('admin_challenges'))

@app.route('/admin/submissions')
@login_required
@admin_required
def admin_submissions():
    db = get_db()
    subs = db.execute('''
        SELECT s.*, u.username, c.title as challenge_title, c.slug
        FROM submissions s
        JOIN users u ON s.user_id = u.id
        JOIN challenges c ON s.challenge_id = c.id
        ORDER BY s.timestamp DESC
    ''').fetchall()
    db.close()
    user = get_current_user()
    return render_template('admin/submissions.html', user=user, submissions=subs)

@app.route('/admin/logs')
@login_required
@admin_required
def admin_logs():
    db = get_db()
    logs = db.execute(
        "SELECT l.*, u.username FROM activity_logs l LEFT JOIN users u ON l.user_id=u.id ORDER BY l.timestamp DESC LIMIT 300"
    ).fetchall()
    db.close()
    user = get_current_user()
    return render_template('admin/logs.html', user=user, logs=logs)

# ── Challenge Routes ───────────────────────────────────────────────────────────

# --- Challenge 1: SQL Injection ---
SQLI_DB = os.path.join(os.path.dirname(__file__), 'challenge_data', 'vuln_login.db')

def init_sqli_db():
    os.makedirs(os.path.dirname(SQLI_DB), exist_ok=True)
    conn = sqlite3.connect(SQLI_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vuln_users
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    if c.execute("SELECT COUNT(*) FROM vuln_users").fetchone()[0] == 0:
        c.execute("INSERT INTO vuln_users VALUES (1,'admin','S3cr3tP4ss!','admin')")
        c.execute("INSERT INTO vuln_users VALUES (2,'alice','alice123','user')")
    conn.commit(); conn.close()

@app.route('/challenges/sqli', methods=['GET','POST'])
@login_required
def challenge_sqli():
    init_sqli_db()
    error = success = query_shown = None
    if request.method == 'POST':
        username = request.form.get('username','')
        password = request.form.get('password','')
        query_shown = f"SELECT * FROM vuln_users WHERE username='{username}' AND password='{password}'"
        log_activity(session.get('user_id'), 'SQLI_ATTEMPT',
                     payload=f'user={username} pass={password}', ip=request.remote_addr)
        try:
            conn = sqlite3.connect(SQLI_DB)
            row = conn.execute(query_shown).fetchone()
            conn.close()
            if row:
                success = FLAGS['sqli']
            else:
                error = 'Invalid credentials.'
        except Exception as e:
            error = f'DB Error: {e}'
    user = get_current_user()
    db = get_db()
    ch = db.execute("SELECT * FROM challenges WHERE slug='sqli'").fetchone()
    db.close()
    return render_template('challenges/sqli.html', user=user, challenge=ch,
                           error=error, success=success, query_shown=query_shown)

# --- Challenge 2: IDOR ---
@app.route('/challenges/idor')
@login_required
def challenge_idor():
    user = get_current_user()
    db = get_db()
    ch = db.execute("SELECT * FROM challenges WHERE slug='idor'").fetchone()
    db.close()
    return render_template('challenges/idor.html', user=user, challenge=ch, profile=None)

@app.route('/challenges/idor/profile')
@login_required
def challenge_idor_profile():
    uid = request.args.get('id', session.get('user_id'))
    try: uid = int(uid)
    except: uid = session.get('user_id')
    log_activity(session.get('user_id'), 'IDOR_ACCESS',
                 payload=f'requested_id={uid}', ip=request.remote_addr)
    db = get_db()
    profile = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    ch = db.execute("SELECT * FROM challenges WHERE slug='idor'").fetchone()
    db.close()
    user = get_current_user()
    return render_template('challenges/idor.html', user=user, challenge=ch, profile=profile)

# --- Challenge 3: XSS ---
@app.route('/challenges/xss', methods=['GET','POST'])
@login_required
def challenge_xss():
    if request.method == 'POST':
        msg = request.form.get('message','')
        db = get_db()
        db.execute("INSERT INTO xss_messages (username, message) VALUES (?,?)",
                   (session['username'], msg))
        db.commit()
        db.close()
        log_activity(session.get('user_id'), 'XSS_POST',
                     payload=msg[:200], ip=request.remote_addr)
        return redirect(url_for('challenge_xss'))
    db = get_db()
    messages = db.execute("SELECT * FROM xss_messages ORDER BY timestamp DESC LIMIT 20").fetchall()
    ch = db.execute("SELECT * FROM challenges WHERE slug='xss'").fetchone()
    db.close()
    user = get_current_user()
    resp = make_response(render_template('challenges/xss.html',
                                         user=user, challenge=ch, messages=messages))
    resp.set_cookie('ctf_flag', FLAGS['xss'], httponly=False, samesite='Lax')
    return resp

# --- Challenge 4: Command Injection ---
CMDI_DIR = os.path.join(os.path.dirname(__file__), 'challenge_data', 'cmdi')

def init_cmdi():
    os.makedirs(CMDI_DIR, exist_ok=True)
    flag_file = os.path.join(CMDI_DIR, 'flag.txt')
    if not os.path.exists(flag_file):
        with open(flag_file, 'w') as f:
            f.write(FLAGS['cmdi'])

@app.route('/challenges/cmdi', methods=['GET','POST'])
@login_required
def challenge_cmdi():
    init_cmdi()
    output = None
    if request.method == 'POST':
        host = request.form.get('host','')
        log_activity(session.get('user_id'), 'CMDI_ATTEMPT',
                     payload=host[:200], ip=request.remote_addr)
        try:
            result = subprocess.run(
                f'ping -c 2 {host}',
                shell=True, capture_output=True, text=True, timeout=8, cwd=CMDI_DIR
            )
            output = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            output = 'Request timed out.'
        except Exception as e:
            output = str(e)
    db = get_db()
    ch = db.execute("SELECT * FROM challenges WHERE slug='cmdi'").fetchone()
    db.close()
    user = get_current_user()
    return render_template('challenges/cmdi.html', user=user, challenge=ch, output=output)

# --- Challenge 5: File Upload ---
UPLOAD_VULN_DIR = os.path.join(os.path.dirname(__file__), 'challenge_data', 'upload')

def init_upload():
    os.makedirs(UPLOAD_VULN_DIR, exist_ok=True)
    flag_file = os.path.join(UPLOAD_VULN_DIR, 'secret_flag.txt')
    if not os.path.exists(flag_file):
        with open(flag_file, 'w') as f:
            f.write(FLAGS['upload'])

@app.route('/challenges/upload', methods=['GET','POST'])
@login_required
def challenge_upload():
    init_upload()
    result = None
    if request.method == 'POST':
        f = request.files.get('avatar')
        if not f or f.filename == '':
            flash('No file selected.', 'error')
            return redirect(url_for('challenge_upload'))
        filename = f.filename
        _, ext = os.path.splitext(filename)
        log_activity(session.get('user_id'), 'UPLOAD_ATTEMPT',
                     payload=f'filename={filename}', ip=request.remote_addr)
        allowed = {'.png','.jpg','.jpeg','.gif'}
        if ext.lower() not in allowed:
            flash(f'Only image files allowed. Got: {ext}', 'error')
        else:
            save_path = os.path.join(UPLOAD_VULN_DIR, filename)
            f.save(save_path)
            # VULNERABLE: executes file if it contains .py anywhere in name
            if '.py' in filename:
                try:
                    out = subprocess.run(
                        ['python3', save_path],
                        capture_output=True, text=True, timeout=5, cwd=UPLOAD_VULN_DIR
                    )
                    result = out.stdout + out.stderr
                except Exception as e:
                    result = str(e)
            else:
                result = f'File uploaded successfully: {filename}'
    db = get_db()
    ch = db.execute("SELECT * FROM challenges WHERE slug='upload'").fetchone()
    db.close()
    user = get_current_user()
    return render_template('challenges/upload.html', user=user, challenge=ch, result=result)

# --- Challenge 6: Broken Access Control ---
@app.route('/challenges/bac')
@login_required
def challenge_bac():
    user = get_current_user()
    db = get_db()
    ch = db.execute("SELECT * FROM challenges WHERE slug='bac'").fetchone()
    db.close()
    return render_template('challenges/bac.html', user=user, challenge=ch, flag=None)

@app.route('/challenges/bac/secret-panel')
@login_required   # ← only login_required, NOT admin_required — that's the vulnerability
def challenge_bac_secret():
    log_activity(session.get('user_id'), 'BAC_ACCESS',
                 payload='accessed /secret-panel', ip=request.remote_addr)
    user = get_current_user()
    db = get_db()
    ch = db.execute("SELECT * FROM challenges WHERE slug='bac'").fetchone()
    db.close()
    return render_template('challenges/bac.html', user=user, challenge=ch, flag=FLAGS['bac'])

# --- Challenge 7: Cryptography ---
def rot13(text):
    result = []
    for c in text:
        if c.isalpha():
            base = ord('a') if c.islower() else ord('A')
            result.append(chr((ord(c) - base + 13) % 26 + base))
        else:
            result.append(c)
    return ''.join(result)

@app.route('/challenges/crypto', methods=['GET','POST'])
@login_required
def challenge_crypto():
    decoded = correct = None
    user_input = ''
    if request.method == 'POST':
        user_input = request.form.get('decoded','').strip()
        decoded = rot13(CRYPTO_ENCODED)
        log_activity(session.get('user_id'), 'CRYPTO_ATTEMPT',
                     payload=user_input[:200], ip=request.remote_addr)
        correct = (user_input == FLAGS['crypto'])
    db = get_db()
    ch = db.execute("SELECT * FROM challenges WHERE slug='crypto'").fetchone()
    db.close()
    user = get_current_user()
    return render_template('challenges/crypto.html', user=user, challenge=ch,
                           encoded=CRYPTO_ENCODED, decoded=decoded,
                           correct=correct, user_input=user_input)

# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
