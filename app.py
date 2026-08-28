from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Temporary storage for visitor logs
visitors = []

@app.route('/')
def index():
    return render_template('index.html', visitors=visitors)

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
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
    
