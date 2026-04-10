from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
import random
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'smartqueue_secret')

# Use environment variable for database path, fallback to local file
DB = os.getenv('DATABASE_PATH', 'database.db')


# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT,
            phone TEXT,
            role TEXT
        )
        """)
        # ensure legacy databases gain phone column
        cur.execute("PRAGMA table_info(users)")
        existing = [row[1] for row in cur.fetchall()]
        if 'phone' not in existing:
            cur.execute("ALTER TABLE users ADD COLUMN phone TEXT")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS queue(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token INTEGER,
            name TEXT,
            department TEXT,
            status TEXT,
            time TEXT,
            date TEXT DEFAULT (date('now'))
        )
        """)

        # Add date column to existing tables if it doesn't exist
        cur.execute("PRAGMA table_info(queue)")
        existing = [row[1] for row in cur.fetchall()]
        if 'date' not in existing:
            cur.execute("ALTER TABLE queue ADD COLUMN date TEXT")
            # Update existing records with current date
            cur.execute("UPDATE queue SET date = date('now') WHERE date IS NULL")

        # Create archive table for historical data
        cur.execute("""
        CREATE TABLE IF NOT EXISTS queue_archive(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token INTEGER,
            name TEXT,
            department TEXT,
            status TEXT,
            time TEXT,
            date TEXT,
            archived_date TEXT DEFAULT (datetime('now'))
        )
        """)

        conn.commit()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")


init_db()

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        role = request.form.get("role", "student")
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validation
        if not all([name, email, phone, role, password, confirm_password]):
            error = "All fields are required"
        elif password != confirm_password:
            error = "Passwords do not match"
        else:
            conn = get_db()
            cur = conn.cursor()
            
            # Check if email already exists
            cur.execute("SELECT * FROM users WHERE email=?", (email,))
            if cur.fetchone():
                error = "Email already registered"
            else:
                cur.execute(
                    "INSERT INTO users(name,email,phone,password,role) VALUES(?,?,?,?,?)",
                    (name, email, phone, password, role),
                )
                conn.commit()
                conn.close()
                return redirect("/login")
            conn.close()

    return render_template("register.html", error=error)


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password),
        )
        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = user[1]
            session["role"] = user[4]

            if user[4] == "admin":
                return redirect("/admin")
            else:
                return redirect("/student")

    return render_template("login.html")


# ---------------- STUDENT DASHBOARD ----------------
@app.route("/student", methods=["GET", "POST"])
def student():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        department = request.form["department"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT MAX(token) FROM queue")
        last = cur.fetchone()[0]
        token = 1 if last is None else last + 1

        cur.execute(
            "INSERT INTO queue(token,name,department,status,time) VALUES(?,?,?,?,?)",
            (
                token,
                session["user"],
                department,
                "Waiting",
                datetime.now().strftime("%H:%M"),
            ),
        )

        conn.commit()
        conn.close()

    # allow simple search in history
    search = request.args.get("search", "").strip()
    conn = get_db()
    cur = conn.cursor()
    if search:
        likeval = f"%{search}%"
        cur.execute("SELECT * FROM queue WHERE name LIKE ? OR token LIKE ? ORDER BY id DESC LIMIT 5", (likeval, likeval))
    else:
        cur.execute("SELECT * FROM queue ORDER BY id DESC LIMIT 5")
    queue = cur.fetchall()

    # stats for student
    cur.execute("SELECT COUNT(*) FROM queue WHERE name=?", (session['user'],))
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM queue WHERE name=? AND (status='Waiting' OR status='Serving')", (session['user'],))
    waiting = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM queue WHERE name=? AND (status='Served' OR status='Completed')", (session['user'],))
    served = cur.fetchone()[0]
    conn.close()

    return render_template("student_dashboard.html", queue=queue, stats={
        'total': total, 'waiting': waiting, 'served': served
    })


# ---------------- MY QUEUE STATUS ----------------
@app.route("/my_queue_status")
def my_queue_status():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    
    # Get all active queues for the current student (not yet served)
    cur.execute("SELECT * FROM queue WHERE name=? AND status!='Served' ORDER BY id DESC", (session['user'],))
    queues = cur.fetchall()
    
    conn.close()
    
    return render_template("my_queue_status.html", queues=queues, get_queue_position=lambda token, dept: get_position_in_queue(token, dept))


def get_position_in_queue(token, department):
    """Get the position of a token in its department's queue"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM queue WHERE department=? AND status='Waiting' AND token<=?", (department, token))
    position = cur.fetchone()[0]
    conn.close()
    return position


# ---------------- STUDENT PROFILE ----------------
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    
    # Get user data
    cur.execute("SELECT * FROM users WHERE name=?", (session['user'],))
    user_data = cur.fetchone()
    
    # Get student queue statistics
    cur.execute("SELECT COUNT(*) FROM queue WHERE name=?", (session['user'],))
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM queue WHERE name=? AND (status='Waiting' OR status='Serving')", (session['user'],))
    waiting = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM queue WHERE name=? AND (status='Served' OR status='Completed')", (session['user'],))
    served = cur.fetchone()[0]
    
    conn.close()
    
    from datetime import date
    today = date.today().strftime("%B %d, %Y")
    
    return render_template("student_profile.html", user_data=user_data, stats={
        'total': total, 'waiting': waiting, 'served': served
    }, member_since=today)


# ---------------- LEAVE QUEUE ----------------
@app.route("/leave_queue/<int:id>")
def leave_queue(id):
    if "user" not in session:
        return redirect("/login")
    
    conn = get_db()
    cur = conn.cursor()
    
    # Delete the queue entry
    cur.execute("DELETE FROM queue WHERE id=?", (id,))
    conn.commit()
    conn.close()
    
    return redirect("/my_queue_status")


# ---------------- MARK AS SERVED ----------------
@app.route("/mark_served/<int:id>")
def mark_served(id):
    if "user" not in session:
        return redirect("/login")
    
    conn = get_db()
    cur = conn.cursor()
    
    # Check if the queue entry belongs to the current user
    cur.execute("SELECT name FROM queue WHERE id=?", (id,))
    result = cur.fetchone()
    if result and result[0] == session["user"]:
        cur.execute("UPDATE queue SET status='Completed' WHERE id=?", (id,))
        conn.commit()
    
    conn.close()
    
    return redirect("/my_queue_status")


# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
def admin():
    conn = get_db()
    cur = conn.cursor()

    # optional filtering/search
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    query = "SELECT * FROM queue"
    params = []
    clauses = []
    if search:
        clauses.append("(name LIKE ? OR token LIKE ?)")
        likeval = f"%{search}%"
        params.extend([likeval, likeval])
    if status:
        clauses.append("status=?")
        params.append(status)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY id"

    cur.execute(query, params)
    queue = cur.fetchall()

    # compute stats
    cur.execute("SELECT COUNT(*) FROM queue")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM queue WHERE status='Waiting' OR status='Serving'")
    waiting = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM queue WHERE status='Served' OR status='Completed'")
    served = cur.fetchone()[0]

    conn.close()

    return render_template("admin_dashboard.html", queue=queue, stats={
        'total': total, 'waiting': waiting, 'served': served
    })


# ---------------- UPDATE STATUS ----------------
@app.route("/update/<int:id>/<status>")
def update_status(id, status):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE queue SET status=? WHERE id=?", (status, id))
    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- CLEAR HISTORY ----------------
@app.route("/clear_history")
def clear_history():
    if "user" not in session or session.get("role") != "admin":
        return redirect("/login")
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Move today's records to archive
    cur.execute("""
        INSERT INTO queue_archive (token, name, department, status, time, date)
        SELECT token, name, department, status, time, date 
        FROM queue 
        WHERE date(date) = date(?)
    """, (today,))
    
    # Delete today's records from main queue
    cur.execute("DELETE FROM queue WHERE date(date) = date(?)", (today,))
    
    # Note: We don't reset the token sequence to maintain uniqueness across days
    
    conn.commit()
    conn.close()
    
    return redirect("/admin")


# ---------------- LIVE QUEUE DISPLAY ----------------
@app.route("/live")
def live_queue():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM queue ORDER BY id")
    queue = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM queue")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM queue WHERE status='Waiting' OR status='Serving'")
    waiting = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM queue WHERE status='Served' OR status='Completed'")
    served = cur.fetchone()[0]

    conn.close()

    # AI Prediction
    peak_hour = ai_peak_hour()

    hours = ["9AM", "10AM", "11AM", "12PM", "1PM", "2PM", "3PM"]
    visitors = [random.randint(5, 50) for _ in range(7)]

    # Get current user info for highlighting
    current_user = session.get('user', None)
    user_role = session.get('role', None)

    return render_template(
        "live_queue.html",
        queue=queue,
        total=total,
        waiting=waiting,
        served=served,
        peak_hour=peak_hour,
        hours=hours,
        visitors=visitors,
        current_user=current_user,
        user_role=user_role,
    )


# ---------------- ANALYTICS ----------------
@app.route("/analytics")
def analytics():
    conn = get_db()
    cur = conn.cursor()

    # Current day stats
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT COUNT(*) FROM queue WHERE date(date) = date(?)", (today,))
    total_today = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM queue WHERE (status='Waiting' OR status='Serving') AND date(date) = date(?)", (today,))
    waiting_today = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM queue WHERE (status='Served' OR status='Completed') AND date(date) = date(?)", (today,))
    served_today = cur.fetchone()[0]

    # All-time stats (including archive)
    cur.execute("SELECT COUNT(*) FROM queue")
    total_all = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM queue_archive")
    archived_count = cur.fetchone()[0]

    total_all += archived_count

    conn.close()

    return render_template(
        "analytics.html",
        total=total_today,
        waiting=waiting_today,
        served=served_today,
        total_all=total_all,
        archived_count=archived_count,
    )


# ---------------- ADMIN ANALYTICS ----------------
@app.route("/admin_analytics")
def admin_analytics():
    conn = get_db()
    cur = conn.cursor()

    # Current active users and tokens
    cur.execute("SELECT COUNT(DISTINCT name) FROM queue")
    users_active = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM queue")
    tokens_active = cur.fetchone()[0]

    # Archive stats
    cur.execute("SELECT COUNT(DISTINCT name) FROM queue_archive")
    users_archive = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM queue_archive")
    tokens_archive = cur.fetchone()[0]

    # Combined stats
    total_users = users_active + users_archive
    total_tokens = tokens_active + tokens_archive

    conn.close()

    peak_hour = ai_peak_hour()
    hours = ["9AM", "10AM", "11AM", "12PM", "1PM", "2PM", "3PM"]
    data = [random.randint(5, 50) for _ in range(7)]

    return render_template(
        "admin_analytics.html",
        users=total_users,
        tokens=total_tokens,
        users_active=users_active,
        tokens_active=tokens_active,
        users_archive=users_archive,
        tokens_archive=tokens_archive,
        peak_hour=peak_hour,
        hours=hours,
        data=data,
    )


# ---------------- AI PREDICTION ----------------
def ai_peak_hour():
    hours = [
        "9 AM - 10 AM",
        "10 AM - 11 AM",
        "11 AM - 12 PM",
        "12 PM - 1 PM",
        "1 PM - 2 PM",
        "2 PM - 3 PM",
    ]
    return random.choice(hours)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- RUN ----------------
@app.errorhandler(404)
def not_found(error):
    return render_template("index.html"), 404


@app.errorhandler(500)
def server_error(error):
    return f"Server Error: {error}", 500


if __name__ == "__main__":
    # Run with gunicorn in production, debug in development
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)