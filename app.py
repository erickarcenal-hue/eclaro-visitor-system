from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Example structure if you are using a Python list as a temporary database
# (If using MongoDB or SQLite, adapt this to update your specific DB record)
visitors_db = []

@app.route('/')
def index():
    return render_template('index.html', success=False)

@app.route('/add', methods=['POST'])
def add_visitor():
    name = request.form.get('name')
    contact = request.form.get('contact')
    purpose = request.form.get('purpose')
    person_to_visit = request.form.get('person_to_visit')
    checkin_date = request.form.get('checkin_date')
    checkin_time = request.form.get('checkin_time')
    
    # Generate a simple QR code URL (using an external API or your existing logic)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Visitor:{name}"
    
    visitor_data = {
        "id": len(visitors_db), # Simple ID tracker
        "name": name,
        "contact": contact,
        "purpose": purpose,
        "person_to_visit": person_to_visit,
        "checkin_date": checkin_date,
        "checkin_time": checkin_time,
        "checkout_time": "-", # Initially blank/dash until time-out
        "status": "Checked-in",
        "qr_url": qr_url
    }
    
    visitors_db.append(visitor_data)
    return render_template('index.html', success=True, visitor=visitor_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Simple mock authentication (change according to your system setup)
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
    
    # Find visitor by ID and update checkout time
    current_time = datetime.now().strftime('%I:%M %p - %b %d, %Y')
    for v in visitors_db:
        if v['id'] == visitor_id:
            v['checkout_time'] = current_time
            v['status'] = 'Checked-out'
            break
            
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
