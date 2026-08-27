import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Function para kumonekta sa database file
def get_db_connection():
    conn = sqlite3.connect('visitors.db')
    conn.row_factory = sqlite3.Row
    return conn

# Gumawa ng database table kung wala pa
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            purpose TEXT NOT NULL,
            person_to_visit TEXT NOT NULL,
            check_in TEXT NOT NULL,
            status TEXT DEFAULT 'Inside Campus'
        )
    ''')
    conn.commit()
    conn.close()

# I-initialize ang DB sa simula
init_db()

@app.route('/')
def home():
    conn = get_db_connection()
    visitors = conn.execute('SELECT * FROM visitors').fetchall()
    conn.close()
    return render_template('index.html', visitors=visitors)

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    purpose = request.form.get('purpose')
    person_to_visit = request.form.get('person_to_visit')
    check_in_time = datetime.now().strftime("%I:%M %p")

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO visitors (name, purpose, person_to_visit, check_in, status) VALUES (?, ?, ?, ?, ?)',
        (name, purpose, person_to_visit, check_in_time, 'Inside Campus')
    )
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/checkout/<int:visitor_id>')
def checkout(visitor_id):
    conn = get_db_connection()
    conn.execute('UPDATE visitors SET status = ? WHERE id = ?', ('Checked Out', visitor_id))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
