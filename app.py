from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'eclaro_secret_key_123'  # Key para sa session management

# Accounts (Username: Password)
USERS = {
    "admin": "admin123",       # Admin Account
    "registrar": "eclaro2026"  # Registrar Account
}

# Temporary in-memory storage para sa visitor logs
visitors = []

# PUBLIC ROUTE: Registration Form lang ang makikita ng visitors
@app.route('/')
def index():
    return render_template('index.html')

# ACTION ROUTE: Pag-submit ng Visitor Form
@app.route('/add', methods=['POST'])
def add_visitor():
    name = request.form.get('name')
    contact = request.form.get('contact')
    purpose = request.form.get('purpose')
    person_to_visit = request.form.get('person_to_visit')

    if name and contact and purpose and person_to_visit:
        visitors.append({
            'name': name,
            'contact': contact,
            'purpose': purpose,
            'person_to_visit': person_to_visit
        })
        flash('Successfully Checked In!', 'success')
    
    return redirect(url_for('index'))

# LOGIN ROUTE: Para sa Admin at Registrar
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

# PROTECTED ROUTE: Ikaw at Registrar lang ang makakakita ng logs
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))  # Harang kapag hindi nakalogin
    
    return render_template('dashboard.html', visitors=visitors, user=session['user'])

# LOGOUT ROUTE
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
    
