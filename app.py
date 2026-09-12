from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
import urllib.parse
from openpyxl import Workbook
import io
import os

app = Flask(__name__)
app.secret_key = 'eclaro_academy_secret_key_2026'

# SQLite Database Setup (Permanent File Storage)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visitors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model Table Definition
class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    purpose = db.Column(db.String(100), nullable=False)
    person_to_visit = db.Column(db.String(100), nullable=False)
    checkin_date = db.Column(db.String(50), nullable=False)
    checkin_time = db.Column(db.String(50), nullable=False)
    qr_url = db.Column(db.Text, nullable=False)

# Auto-create the database table upon app starting
with app.app_context():
    db.create_all()

# Allowed Staff Accounts
USERS = {
    "admin": "admin123",
    "registrar": "registrar123"
}

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

    qr_data = f"Name: {name}\nContact: {contact}\nPurpose: {purpose}\nHost: {person_to_visit}\nDate: {checkin_date}\nTime: {checkin_time}"
    encoded_data = urllib.parse.quote(qr_data)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={encoded_data}"

    # Save permanently inside SQLite database
    new_visitor = Visitor(
        name=name,
        contact=contact,
        purpose=purpose,
        person_to_visit=person_to_visit,
        checkin_date=checkin_date,
        checkin_time=checkin_time,
        qr_url=qr_url
    )
    db.session.add(new_visitor)
    db.session.commit()

    return render_template('index.html', success=True, visitor=new_visitor)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip()

        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['user'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials. Please check your username or password.", "error")

    return render_template('login.html')

@app.route('/dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    current_user = session.get('user', 'Staff').capitalize()
    # Fetch all records ordered by newest ID first
    visitors = Visitor.query.order_by(Visitor.id.desc()).all()
    return render_template('dashboard.html', current_user=current_user, visitors=visitors)

@app.route('/export')
def export_excel():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    wb = Workbook()
    ws = wb.active
    ws.title = "Visitor Logs"

    headers = ["Date", "Time", "Visitor Name", "Contact No.", "Purpose", "Destination / Host"]
    ws.append(headers)

    visitors = Visitor.query.order_by(Visitor.id.desc()).all()
    for v in visitors:
        ws.append([
            v.checkin_date,
            v.checkin_time,
            v.name,
            v.contact,
            v.purpose,
            v.person_to_visit
        ])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name='Eclaro_Visitor_Logs.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
