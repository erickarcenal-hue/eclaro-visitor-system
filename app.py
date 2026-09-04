@app.route('/add', methods=['POST'])
def add_visitor():
    name = request.form.get('name')
    contact = request.form.get('contact')
    purpose = request.form.get('purpose')
    person_to_visit = request.form.get('person_to_visit')
    checkin_date = request.form.get('checkin_date') # Bagong field
    checkin_time = request.form.get('checkin_time') # Bagong field

    visitor_data = {
        "name": name,
        "contact": contact,
        "purpose": purpose,
        "person_to_visit": person_to_visit,
        "checkin_date": checkin_date,
        "checkin_time": checkin_time,
        "qr_url": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={name}-{contact}"
    }

    return render_template('index.html', success=True, visitor=visitor_data)
    
