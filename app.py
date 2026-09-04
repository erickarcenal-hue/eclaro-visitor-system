from flask import Flask, render_template, request, redirect, url_for, flash, session
import urllib.parse

app = Flask(__name__)
app.secret_key = 'eclaro_academy_secret_key_2026'

# Allowed Staff & Registrar Accounts
USERS = {
    "admin": "admin123",
    "registrar": "registrar123"
}

# Temporary List to store visitors (In-memory storage)
VISITOR_LOGS = []

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

    visitor_data = {
        "name": name,
        "contact": contact,
        "purpose": purpose,
        "person_to_visit": person_to_visit,
        "checkin_date": checkin_date,
        "checkin_time": checkin_time,
        "qr_url": qr_url
    }

    # I-save sa listahan para makita sa dashboard
    VISITOR_LOGS.insert(0, visitor_data)

    return render_template('index.html', success=True, visitor=visitor_data)

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
    
    # Bumuo tayo ng HTML table para makita ang listahan ng mga nag-check-in
    rows = ""
    if not VISITOR_LOGS:
        rows = "<tr><td colspan='6' style='text-align:center; padding: 20px; color: #94a3b8;'>No visitors checked in yet.</td></tr>"
    else:
        for v in VISITOR_LOGS:
            rows += f"""
            <tr style="border-bottom: 1px solid #1e293b;">
                <td style="padding: 12px; color: #8CC63F; font-weight: 600;">{v['checkin_date']}<br><span style="font-size: 11px; color: #94a3b8;">{v['checkin_time']}</span></td>
                <td style="padding: 12px; font-weight: 600; color: white;">{v['name']}</td>
                <td style="padding: 12px; color: #cbd5e1;">{v['contact']}</td>
                <td style="padding: 12px; color: #cbd5e1;">{v['purpose']}</td>
                <td style="padding: 12px; color: #cbd5e1;">{v['person_to_visit']}</td>
                <td style="padding: 12px;"><span style="background: rgba(140, 198, 63, 0.2); color: #8CC63F; padding: 4px 10px; border-radius: 20px; font-size: 11px;">Checked-in</span></td>
            </tr>
            """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Eclaro Staff Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body style="font-family: 'Poppins', sans-serif; background-color: #031137; color: #f8fafc; padding: 30px;">
        <div style="max-width: 1000px; margin: 0 auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 20px; margin-bottom: 20px;">
                <div>
                    <h1 style="font-size: 24px; font-weight: bold; color: white;">Eclaro Staff Dashboard</h1>
                    <p style="font-size: 12px; color: #94a3b8;">Logged in as: <strong style="color: #8CC63F;">{current_user}</strong></p>
                </div>
                <div>
                    <a href="/" style="background: #1e293b; color: white; padding: 8px 16px; border-radius: 10px; text-decoration: none; font-size: 12px; margin-right: 10px;">Home Form</a>
                    <a href="/logout" style="background: #ef4444; color: white; padding: 8px 16px; border-radius: 10px; text-decoration: none; font-size: 12px;">Logout</a>
                </div>
            </div>

            <h2 style="font-size: 16px; font-weight: 600; margin-bottom: 15px; color: #cbd5e1;"><i class="fas fa-users mr-2 text-[#8CC63F]"></i> Visitor Logs History</h2>
            
            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.3);">
                <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px;">
                    <thead>
                        <tr style="background: #1e293b; color: #94a3b8; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;">
                            <th style="padding: 12px;">Date & Time</th>
                            <th style="padding: 12px;">Visitor Name</th>
                            <th style="padding: 12px;">Contact No.</th>
                            <th style="padding: 12px;">Purpose</th>
                            <th style="padding: 12px;">Destination</th>
                            <th style="padding: 12px;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
    
