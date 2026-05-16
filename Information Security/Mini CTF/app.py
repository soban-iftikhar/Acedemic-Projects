import os
import sqlite3
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, make_response)
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db, init_db
from auth import login_required, admin_required, get_current_user, log_activity
from flags import FLAGS, CRYPTO_ENCODED

app = Flask(__name__)
app.secret_key = os.urandom(32)

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
    if correct:
        db.execute("UPDATE users SET score = score + ? WHERE id=?", (ch['points'], user['id']))
    db.commit()
    db.close()
    
    try:
        log_activity(user['id'], 'FLAG_SUBMIT',
                     payload=f'challenge={slug} flag={submitted} correct={correct}',
                     ip=request.remote_addr)
    except:
        pass  # Ignore logging errors to prevent lockups
    
    if correct:
        msg = f'Correct! +{ch["points"]} pts'
        if first_blood:
            msg += ' 🩸 First Blood!'
        flash(msg, 'success')
    else:
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
    conn = sqlite3.connect(SQLI_DB, timeout=10.0)
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
        conn = None
        try:
            conn = sqlite3.connect(SQLI_DB, timeout=10.0)
            row = conn.execute(query_shown).fetchone()
            if row:
                success = FLAGS['sqli']
            else:
                error = 'Invalid credentials.'
        except Exception as e:
            error = f'DB Error: {e}'
        finally:
            if conn:
                conn.close()
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

# --- Challenge 6: Hash Cracking ---
@app.route('/challenges/hash', methods=['GET', 'POST'])
@login_required
def challenge_hash():
    success = error = None
    db = None
    try:
        db = get_db()
        ch = db.execute("SELECT * FROM challenges WHERE slug='hash'").fetchone()
        if request.method == 'POST':
            cracked = request.form.get('cracked', '').strip().lower()
            db.execute(
                "INSERT INTO activity_logs (user_id, action, payload, ip_address) VALUES (?,?,?,?)",
                (session['user_id'], 'HASH_ATTEMPT', cracked, request.remote_addr)
            )
            if cracked == 'password':
                success = FLAGS['hash']
            else:
                error = 'Incorrect plaintext. That is not what this hash decodes to.'
            db.commit()
    except Exception as e:
        error = f'Error: {e}'
    finally:
        if db: db.close()
    user = get_current_user()
    return render_template('challenges/hash.html', user=user, challenge=ch,
                           success=success, error=error)

# --- Challenge 7: RSA Decryption ---
@app.route('/challenges/rsa', methods=['GET', 'POST'])
@login_required
def challenge_rsa():
    success = error = None
    calc = None
    db = None
    try:
        db = get_db()
        ch = db.execute("SELECT * FROM challenges WHERE slug='rsa'").fetchone()
        if request.method == 'POST':
            action = request.form.get('action', '')
            
            if action == 'calculate':
                try:
                    p  = int(request.form.get('p', 0))
                    q  = int(request.form.get('q', 0))
                    e  = int(request.form.get('e', 0))
                    ct = int(request.form.get('ct', 0))
                    n     = p * q
                    phi_n = (p - 1) * (q - 1)
                    d     = pow(e, -1, phi_n)
                    pt    = pow(ct, d, n)
                    calc  = {'n': n, 'phi_n': phi_n, 'd': d, 'plaintext': pt}
                    db.execute(
                        "INSERT INTO activity_logs (user_id, action, payload, ip_address) VALUES (?,?,?,?)",
                        (session['user_id'], 'RSA_CALC',
                         f'p={p} q={q} e={e} ct={ct} result={pt}', request.remote_addr)
                    )
                except Exception as ex:
                    error = f'Calculation error: {ex}'
            
            elif action == 'submit':
                answer = request.form.get('plaintext', '').strip()
                db.execute(
                    "INSERT INTO activity_logs (user_id, action, payload, ip_address) VALUES (?,?,?,?)",
                    (session['user_id'], 'RSA_ATTEMPT', answer, request.remote_addr)
                )
                if answer in ['65', 'A', 'a']:
                    success = FLAGS['rsa']
                else:
                    error = 'Incorrect. Check your RSA calculation steps.'
            
            db.commit()
    except Exception as e:
        if not error: error = f'Error: {e}'
    finally:
        if db: db.close()
    user = get_current_user()
    return render_template('challenges/rsa.html', user=user, challenge=ch,
                           success=success, error=error, calc=calc)

# --- Challenge 8: Brute Force Login ---
@app.route('/challenges/bruteforce', methods=['GET', 'POST'])
@login_required
def challenge_bruteforce():
    WORDLIST = ['password','123456','admin','letmein','qwerty',
                'monkey','dragon','master','abc123','password123']
    success = error = None
    db = None
    try:
        db = get_db()
        ch = db.execute("SELECT * FROM challenges WHERE slug='bruteforce'").fetchone()
        if request.method == 'POST':
            pwd = request.form.get('password', '').strip()
            db.execute(
                "INSERT INTO activity_logs (user_id, action, payload, ip_address) VALUES (?,?,?,?)",
                (session['user_id'], 'BRUTEFORCE_ATTEMPT', pwd, request.remote_addr)
            )
            if pwd == 'letmein':
                success = FLAGS['bruteforce']
            else:
                error = 'Wrong password. No lockout policy — keep trying.'
            db.commit()
    except Exception as e:
        error = f'Error: {e}'
    finally:
        if db: db.close()
    user = get_current_user()
    return render_template('challenges/bruteforce.html', user=user, challenge=ch,
                           success=success, error=error, wordlist=WORDLIST)

# --- Challenge 9: Diffie-Hellman Exchange ---
@app.route('/challenges/diffie', methods=['GET', 'POST'])
@login_required
def challenge_diffie():
    success = error = None
    calc = None
    db = None
    try:
        db = get_db()
        ch = db.execute("SELECT * FROM challenges WHERE slug='diffie'").fetchone()
        if request.method == 'POST':
            action = request.form.get('action', '')
            
            if action == 'calculate':
                try:
                    p = int(request.form.get('p', 0))
                    g = int(request.form.get('g', 0))
                    A = int(request.form.get('A', 0))
                    a = int(request.form.get('a', 0))
                    shared = pow(A, a, p)
                    calc = {'p': p, 'g': g, 'A': A, 'a': a, 'shared': shared}
                    db.execute(
                        "INSERT INTO activity_logs (user_id, action, payload, ip_address) VALUES (?,?,?,?)",
                        (session['user_id'], 'DH_CALC',
                         f'p={p} g={g} A={A} a={a} shared={shared}', request.remote_addr)
                    )
                except Exception as ex:
                    error = f'Calculation error: {ex}'
            
            elif action == 'submit':
                answer = request.form.get('shared_secret', '').strip()
                db.execute(
                    "INSERT INTO activity_logs (user_id, action, payload, ip_address) VALUES (?,?,?,?)",
                    (session['user_id'], 'DH_ATTEMPT', answer, request.remote_addr)
                )
                if answer == '2':
                    success = FLAGS['diffie']
                else:
                    error = 'Incorrect shared secret. Use: shared = B^a mod p.'
            
            db.commit()
    except Exception as e:
        if not error: error = f'Error: {e}'
    finally:
        if db: db.close()
    user = get_current_user()
    return render_template('challenges/diffie.html', user=user, challenge=ch,
                           success=success, error=error, calc=calc)

# --- Challenge 10: Vigenere Cipher ---
@app.route('/challenges/vigenere', methods=['GET', 'POST'])
@login_required
def challenge_vigenere():
    success = error = None
    db = None
    try:
        db = get_db()
        ch = db.execute("SELECT * FROM challenges WHERE slug='vigenere'").fetchone()
        if request.method == 'POST':
            answer = request.form.get('decoded', '').strip()
            db.execute(
                "INSERT INTO activity_logs (user_id, action, payload, ip_address) VALUES (?,?,?,?)",
                (session['user_id'], 'VIGENERE_ATTEMPT', answer[:100], request.remote_addr)
            )
            if answer.lower() == FLAGS['vigenere'].lower():
                success = FLAGS['vigenere']
            else:
                error = 'Incorrect decryption. Check your key alignment and shift direction.'
            db.commit()
    except Exception as e:
        error = f'Error: {e}'
    finally:
        if db: db.close()
    user = get_current_user()
    return render_template('challenges/vigenere.html', user=user, challenge=ch,
                           success=success, error=error)

# --- Challenge 11: Cryptography ---
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
    decoded = correct_flag = None
    user_input = ''
    if request.method == 'POST':
        user_input = request.form.get('decoded','').strip()
        decoded = rot13(CRYPTO_ENCODED)
        log_activity(session.get('user_id'), 'CRYPTO_ATTEMPT',
                     payload=user_input[:200], ip=request.remote_addr)
        if user_input == FLAGS['crypto']:
            correct_flag = FLAGS['crypto']
    db = get_db()
    ch = db.execute("SELECT * FROM challenges WHERE slug='crypto'").fetchone()
    db.close()
    user = get_current_user()
    return render_template('challenges/crypto.html', user=user, challenge=ch,
                           encoded=CRYPTO_ENCODED, decoded=decoded,
                           correct_flag=correct_flag, user_input=user_input)

# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
