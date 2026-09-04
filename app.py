from flask import Flask, render_template, request, redirect, url_for, session, flash
import urllib.parse

app = Flask(__name__)
app.secret_key = 'eclaro_secret_key_123'

USERS = {
    "admin": "admin123",
    "registrar": "eclaro2026"
}

visitors = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_visitor():
    name = request.form.get('name')
    contact = request.form.get('contact')
    purpose = request.form.get('purpose')
    person_to_visit = request.form.get('person_to_visit')

    if name and contact and purpose and person_to_visit:
        # Gumawa ng natatanging Pass Data para sa QR Code
        qr_data = f"ECLARO VISITOR | Name: {name} | Contact: {contact} | Purpose: {purpose}"
        
        # Pure Python URL Encoding para sa QR Image (Walang JavaScript)
        encoded_data = urllib.parse.quote(qr_data)
        qr_url = f"https://quickchart.io/qr?text={encoded_data}&size=200"

        new_visitor = {
            'name': name,
            'contact': contact,
            'purpose': purpose,
            'person_to_visit': person_to_visit,
            'qr_url': qr_url
        }
        
        visitors.append(new_visitor)
        
        # Ipasa ang visitor data sa confirmation page
        return render_template('index.html', success=True, visitor=new_visitor)
    
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in USERS and USERS[username] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Username or Password', 'error')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', visitors=visitors, user=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
    
