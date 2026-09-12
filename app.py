from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import csv
import io

app = Flask(__name__)
app.secret_key = 'eclaro_academy_secure_secret_key'

visitors_db = []

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/register')
def index():
    return render_template('index.html', success=False)

@app.route('/add', methods=['POST'])
def add_visitor():
    name = request.form.get('name')
    contact = request.form.get('contact')
    
    if not contact or len(contact) != 11 or not contact.isdigit() or not contact.startswith('09'):
        return render_template('index.html', success=False, error="Invalid contact number. Must be exactly 11 digits starting with 09.")
    
    purpose = request.form.get('purpose')
    person_to_visit = request.form.get('person_to_visit')
    scheduled_date = request.form.get('scheduled_date')
    scheduled_time = request.form.get('scheduled_time')
    checkin_date = request.form.get('checkin_date')
    checkin_time = request.form.get('checkin_time')
    
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=EclaroAcademy-Visitor:{name}"
    
    visitor_data = {
        "id": len(visitors_db),
        "name": name,
        "contact": contact,
        "purpose": purpose,
        "person_to_visit": person_to_visit,
        "scheduled_date": scheduled_date if scheduled_date else "Immediate / Walk-in",
        "scheduled_time": scheduled_time if scheduled_time else "-",
        "checkin_date": checkin_date,
        "checkin_time": checkin_time,
        "checkout_time": "-",
        "status": "Scheduled / Checked-in",
        "qr_url": qr_url
    }
    
    visitors_db.append(visitor_data)
    return render_template('index.html', success=True, visitor=visitor_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in ['admin', 'registrar'] and password == 'password123':
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', visitors=visitors_db, current_user=session['user'])

@app.route('/checkout/<int:visitor_id>', methods=['POST'])
def checkout(visitor_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    current_time = datetime.now().strftime('%I:%M %p - %b %d, %Y')
    for v in visitors_db:
        if v['id'] == visitor_id:
            v['checkout_time'] = current_time
            v['status'] = 'Checked-out'
            break
            
    return redirect(url_for('dashboard'))

@app.route('/export')
def export_excel():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Visitor Name', 'Contact No.', 'Purpose', 'Destination', 'Appointment Schedule', 'Time-In', 'Time-Out', 'Status'])
    for v in visitors_db:
        writer.writerow([
            v['name'], 
            v['contact'], 
            v['purpose'], 
            v['person_to_visit'], 
            f"{v['scheduled_date']} {v['scheduled_time']}",
            f"{v['checkin_date']} | {v['checkin_time']}", 
            v['checkout_time'], 
            v['status']
        ])
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=Eclaro_Academy_Visitor_Logs.csv"}
    )

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
