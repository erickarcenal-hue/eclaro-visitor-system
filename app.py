import csv
import io
import sqlite3
from datetime import datetime
from functools import wraps
from flask import (
    Flask,
    Response,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "eclaro_academy_secret_key_2026_2027"


# Database Initialization
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Users Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """
    )

    # Visitor Logs Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS visitor_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            contact_no TEXT NOT NULL,
            purpose TEXT NOT NULL,
            person_to_visit TEXT NOT NULL,
            date_entry TEXT NOT NULL,
            time_in TEXT NOT NULL,
            time_out TEXT DEFAULT 'ON CAMPUS',
            status TEXT DEFAULT 'ACTIVE'
        )
    """
    )

    # Insert default Guard and Admin accounts if not existing
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", generate_password_hash("admin123"), "ADMIN"),
        )
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("guard", generate_password_hash("guard123"), "GUARD"),
        )

    conn.commit()
    conn.close()


init_db()


# Login Required Decorator (Security Check)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Kailangan mong mag-login muna.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# --- ROUTES ---


# 1. Public Visitor Check-In Form
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        full_name = request.form["full_name"]
        contact_no = request.form["contact_no"]
        purpose = request.form["purpose"]
        person_to_visit = request.form["person_to_visit"]
        privacy_consent = request.form.get("privacy_consent")

        if not privacy_consent:
            flash(
                "Kailangang pumayag sa Data Privacy Consent bago makapag-submit.",
                "danger",
            )
            return render_template("index.html", success=False)

        now = datetime.now()
        date_entry = now.strftime("%Y-%m-%d")
        time_in = now.strftime("%I:%M %p")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO visitor_logs (full_name, contact_no, purpose, person_to_visit, date_entry, time_in)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (full_name, contact_no, purpose, person_to_visit, date_entry, time_in),
        )
        conn.commit()
        conn.close()

        return render_template(
            "index.html",
            success=True,
            msg="Matagumpay na na-record ang inyong pagpasok sa Eclaro Academy!",
        )

    return render_template("index.html", success=False)


# 2. Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[3]

            if user[3] == "ADMIN":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("guard_dashboard"))
        else:
            flash("Maling username o password.", "danger")

    return render_template("login.html")


# 3. Guard Dashboard
@app.route("/guard")
@login_required
def guard_dashboard():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, full_name, purpose, person_to_visit, time_in FROM visitor_logs WHERE status = 'ACTIVE' ORDER BY id DESC"
    )
    active_visitors = cursor.fetchall()
    conn.close()
    return render_template(
        "guard_dashboard.html",
        visitors=active_visitors,
        username=session["username"],
    )


# 4. Visitor Check-Out Action
@app.route("/checkout/<int:visitor_id>")
@login_required
def checkout(visitor_id):
    time_out = datetime.now().strftime("%I:%M %p")
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE visitor_logs SET time_out = ?, status = 'COMPLETED' WHERE id = ?",
        (time_out, visitor_id),
    )
    conn.commit()
    conn.close()
    flash("Naka-check out na ang bisita.", "info")
    return redirect(url_for("guard_dashboard"))


# 5. Admin Dashboard
@app.route("/admin")
@login_required
def admin_dashboard():
    if session.get("role") != "ADMIN":
        flash("Access Denied: Para lamang sa Administrators.", "danger")
        return redirect(url_for("guard_dashboard"))

    search_query = request.args.get("search", "")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if search_query:
        cursor.execute(
            """
            SELECT * FROM visitor_logs 
            WHERE full_name LIKE ? OR purpose LIKE ? OR person_to_visit LIKE ? OR date_entry LIKE ?
            ORDER BY id DESC
        """,
            (
                f"%{search_query}%",
                f"%{search_query}%",
                f"%{search_query}%",
                f"%{search_query}%",
            ),
        )
    else:
        cursor.execute("SELECT * FROM visitor_logs ORDER BY id DESC")

    all_logs = cursor.fetchall()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        logs=all_logs,
        search=search_query,
        username=session["username"],
    )


# 6. EXPORT LOGS TO CSV (Bagong Feature)
@app.route("/export_csv")
@login_required
def export_csv():
    if session.get("role") != "ADMIN":
        return redirect(url_for("guard_dashboard"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM visitor_logs ORDER BY id DESC")
    logs = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "ID",
            "Full Name",
            "Contact No.",
            "Purpose",
            "Person to Visit",
            "Date Entry",
            "Time In",
            "Time Out",
            "Status",
        ]
    )

    for log in logs:
        writer.writerow(log)

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment;filename=eclaro_visitor_logs.csv"
        },
    )


# 7. Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Naka-logout ka na.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
    
