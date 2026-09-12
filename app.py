from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import random
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
app.secret_key = 'eclaro_vms_secret_key_2026'

# --- GOOGLE SHEETS SETUP ---
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_sheet():
    """ Connect to Google Sheets """
    try:
        creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        client = gspread.authorize(creds)
        # Pangalan ng Google Sheet na ginawa mo
        sheet = client.open("Eclaro_Visitor_Logs").sheet1
        return sheet
    except Exception as e:
        print(f"Google Sheet Connection Error: {e}")
        return None

# Temporary local backup list
visitor_logs = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('fullName')
    phone = request.form.get('contactNumber')
    purpose = request.form.get('purpose')
    department = request.form.get('department')
    
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
    
    # 1. Local list update
    visitor_logs.insert(0, new_visitor)
    
    # 2. AUTO-SAVE TO GOOGLE SHEET
    sheet = get_sheet()
    if sheet:
        row = [pass_id, name, phone, purpose, department, entry_time, 'Inside']
        sheet.append_row(row)
    
    return render_template('index.html', gate_pass=new_visitor)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            session['user'] = 'Staff/Guard'
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Magbasa ng logs mula sa Google Sheet kung available
    sheet = get_sheet()
    display_logs = []
    
    if sheet:
        try:
            records = sheet.get_all_records()
            for r in reversed(records):
                display_logs.append({
                    'id': r.get('Pass ID'),
                    'name': r.get('Full Name'),
                    'phone': r.get('Contact Number'),
                    'purpose': r.get('Purpose'),
                    'department': r.get('Department'),
                    'time': r.get('Date & Time'),
                    'status': r.get('Status')
                })
        except Exception:
            display_logs = visitor_logs
    else:
        display_logs = visitor_logs
        
    total_registered = len(display_logs)
    currently_inside = sum(1 for v in display_logs if v['status'] == 'Inside')
    checked_out = sum(1 for v in display_logs if v['status'] == 'Checked Out')
    
    stats = {
        'total': total_registered,
        'inside': currently_inside,
        'out': checked_out
    }
    
    return render_template('dashboard.html', logs=display_logs, stats=stats)

@app.route('/toggle-status/<pass_id>')
def toggle_status(pass_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    sheet = get_sheet()
    if sheet:
        try:
            cell = sheet.find(pass_id)
            if cell:
                current_val = sheet.cell(cell.row, 7).value
                new_status = 'Checked Out' if current_val == 'Inside' else 'Inside'
                sheet.update_cell(cell.row, 7, new_status)
        except Exception as e:
            print(f"Error updating status in sheet: {e}")
            
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
