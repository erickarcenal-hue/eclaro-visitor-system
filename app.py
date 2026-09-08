import sqlite3
import csv
import io
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response

app = Flask(__name__)
app.secret_key = 'eclaro_academy_secret_key_2026'

# Initialize Database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Visitor logs table
    cursor.execute('''
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
    ''')
    conn.commit()
    conn.close()

init_db()

# --- ROUTES ---

# 1. Visitor Registration Form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        contact_no = request.form.get('contact_no')
        purpose = request.form.get('purpose')
        person_to_visit = request.form.get('person_to_visit')
        privacy_consent = request.form.get('privacy_consent')

        if not privacy_consent:
            flash("You must agree to the Data Privacy Consent before submitting.", "danger")
            return render_template('index.html', success=False)

        now = datetime.now()
        date_entry = now.strftime("%Y-%m-%d")
        time_in = now.strftime("%I:%M %p")

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO visitor_logs (full_name, contact_no, purpose, person_to_visit, date_entry, time_in)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (full_name, contact_no, purpose, person_to_visit, date_entry, time_in))
        conn.commit()
        conn.close()

        return render_template('index.html', success=True, msg="Your visitor check-in has been successfully recorded!")

    return render_template('index.html', success=False)

# 2. Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Admin Credential Check
        if username == 'admin' and password == 'adminpassword':
            session['user'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials. Use 'admin' and 'adminpassword'.", "danger")

    return render_template('login.html')

# 3. Admin Dashboard
@app.route('/admin')
def admin_dashboard():
    if session.get('user') != 'admin':
        return redirect(url_for('login'))

    search_query = request.args.get('search', '')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if search_query:
        cursor.execute('''
            SELECT * FROM visitor_logs 
            WHERE full_name LIKE ? OR purpose LIKE ? OR person_to_visit LIKE ? OR date_entry LIKE ?
            ORDER BY id DESC
        ''', (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
    else:
        cursor.execute('SELECT * FROM visitor_logs ORDER BY id DESC')

    logs = cursor.fetchall()
    conn.close()

    return render_template('admin.html', logs=logs, search=search_query)

# 4. Check-out Visitor
@app.route('/checkout/<int:visitor_id>')
def checkout(visitor_id):
    if session.get('user') != 'admin':
        return redirect(url_for('login'))

    time_out = datetime.now().strftime("%I:%M %p")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE visitor_logs SET time_out = ?, status = 'COMPLETED' WHERE id = ?", (time_out, visitor_id))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

# 5. Export CSV
@app.route('/export_csv')
def export_csv():
    if session.get('user') != 'admin':
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM visitor_logs ORDER BY id DESC")
    logs = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Full Name', 'Contact No', 'Purpose', 'Person to Visit', 'Date', 'Time In', 'Time Out', 'Status'])

    for log in logs:
        writer.writerow(log)

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=eclaro_visitor_logs.csv"}
    )

# 6. Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
    
