from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database initialization function
def init_db():
    conn = sqlite3.connect('visitors.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            purpose TEXT NOT NULL,
            person_to_visit TEXT NOT NULL,
            scheduled_date TEXT NOT NULL,
            scheduled_time TEXT NOT NULL,
            checkin_date TEXT,
            checkin_time TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Route para sa Welcome/Home page
@app.route('/')
def home():
    return render_template('welcome.html')

# Route para sa Registration page (Wizard)
@app.route('/register')
def register():
    return render_template('index.html', success=False)

# Route para i-handle ang pag-submit ng form
@app.route('/add', methods=['POST'])
def add_visitor():
    name = request.form.get('name')
    contact = request.form.get('contact')
    purpose = request.form.get('purpose')
    person_to_visit = request.form.get('person_to_visit')
    scheduled_date = request.form.get('scheduled_date')
    scheduled_time = request.form.get('scheduled_time')
    checkin_date = request.form.get('checkin_date')
    checkin_time = request.form.get('checkin_time')

    # I-save sa SQLite database
    conn = sqlite3.connect('visitors.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO visitors (name, contact, purpose, person_to_visit, scheduled_date, scheduled_time, checkin_date, checkin_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, contact, purpose, person_to_visit, scheduled_date, scheduled_time, checkin_date, checkin_time))
    conn.commit()
    conn.close()

    # Data para sa success pass preview sa template
    visitor_data = {
        'name': name,
        'contact': contact,
        'purpose': purpose,
        'person_to_visit': person_to_visit,
        'scheduled_date': scheduled_date,
        'scheduled_time': scheduled_time
    }

    return render_template('index.html', success=True, visitor=visitor_data)

# Route para sa Admin Dashboard
@app.route('/admin')
def admin():
    conn = sqlite3.connect('visitors.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM visitors ORDER BY id DESC')
    visitors = cursor.fetchall()
    conn.close()
    
    return render_template('admin.html', visitors=visitors)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
