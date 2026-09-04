from flask import Flask, render_template, request, redirect, url_for, flash, session
import urllib.parse

app = Flask(__name__)
app.secret_key = 'eclaro_academy_secret_key_2026'

# Dummy Credentials for Staff Portal
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_visitor():
    name = request.form.get('name', '').strip()
    contact = request.form.get('contact', '').strip()
    purpose = request.form.get('purpose', '').strip()
    person_to_visit = request.form.get('person_to_visit', '').strip()
    checkin_date = request.form.get('checkin_date', '')
    checkin_time = request.form.get('checkin_time', '')

    # Generate QR Code URL
    qr_data = f"Name: {name}\nContact: {contact}\nPurpose: {purpose}\nHost: {person_to_visit}\nDate: {checkin_date}\nTime: {checkin_time}"
    encoded_data = urllib.parse.quote(qr_data)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={encoded_data}"

    visitor_data = {
        "name": name,
        "contact": contact,
        "purpose": purpose,
        "person_to_visit": person_to_visit,
        "checkin_date": checkin_date,
        "checkin_time": checkin_time,
        "qr_url": qr_url
    }

    return render_template('index.html', success=True, visitor=visitor_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USER and password == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials. Please try again.", "error")

    return render_template('login.html')

@app.route('/dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return "<h1>Eclaro Staff Dashboard (SY 2026-2027)</h1><p>Welcome, Authorized Personnel.</p><a href='/logout'>Logout</a>"

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
    
