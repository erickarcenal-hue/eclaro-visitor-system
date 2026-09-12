from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'eclaro_vms_secret_key_2026'  # Secret key para sa session management

# Temporary In-Memory Data Store
visitor_logs = []

@app.route('/')
def index():
    """ Visitor Registration Page (Kiosk View) """
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    """ Process Visitor Form Submission """
    name = request.form.get('fullName')
    phone = request.form.get('contactNumber')
    purpose = request.form.get('purpose')
    department = request.form.get('department')
    
    # Generate Unique Pass ID
    pass_id = f"ECL-{random.randint(100000, 999999)}"
    entry_time = datetime.now().strftime("%b %d, %Y - %I:%M %p")
    
    new_visitor = {
        'id': pass_id,
        'name': name,
        'phone': phone,
        'purpose': purpose,
        'department': department,
        'time': entry_time,
        'status': 'Inside'
    }
    
    visitor_logs.insert(0, new_visitor)
    
    # Render index with pass modal data
    return render_template('index.html', gate_pass=new_visitor)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Staff Login Page """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple Authentication (Default: admin / admin)
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            session['user'] = 'Staff/Guard'
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """ Staff Dashboard / Logs Management """
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    total_registered = len(visitor_logs)
    currently_inside = sum(1 for v in visitor_logs if v['status'] == 'Inside')
    checked_out = sum(1 for v in visitor_logs if v['status'] == 'Checked Out')
    
    stats = {
        'total': total_registered,
        'inside': currently_inside,
        'out': checked_out
    }
    
    return render_template('dashboard.html', logs=visitor_logs, stats=stats)

@app.route('/toggle-status/<pass_id>')
def toggle_status(pass_id):
    """ Change Visitor Status (Check Out / Re-enter) """
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    for visitor in visitor_logs:
        if visitor['id'] == pass_id:
            visitor['status'] = 'Checked Out' if visitor['status'] == 'Inside' else 'Inside'
            break
            
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    """ Logout Staff """
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
