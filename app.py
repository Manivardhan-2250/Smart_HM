from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
def connect_db():
    return sqlite3.connect("database.db")

def init_db():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS patients(id INTEGER PRIMARY KEY, name TEXT, age TEXT, disease TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS doctors(id INTEGER PRIMARY KEY, name TEXT, specialization TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS appointments(id INTEGER PRIMARY KEY, patient TEXT, doctor TEXT, date TEXT)")

    conn.commit()
    conn.close()

init_db()

# ---------------- AI MODEL ----------------
def predict_specialization(symptom):
    symptom = symptom.lower()

    if "fever" in symptom or "cold" in symptom:
        return "General Physician"
    elif "heart" in symptom:
        return "Cardiologist"
    elif "skin" in symptom:
        return "Dermatologist"
    elif "eye" in symptom:
        return "Ophthalmologist"
    elif "bone" in symptom:
        return "Orthopedic"
    else:
        return "General Physician"

# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        if user == "admin" and pwd == "1234":
            session['user'] = user
            return redirect('/dashboard')
        else:
            return "Invalid Credentials"

    return render_template('login.html')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    conn = connect_db()
    cur = conn.cursor()

    patients = cur.execute("SELECT * FROM patients").fetchall()
    doctors = cur.execute("SELECT * FROM doctors").fetchall()
    appointments = cur.execute("SELECT * FROM appointments").fetchall()

    conn.close()

    return render_template('dashboard.html',
                           patients=patients,
                           doctors=doctors,
                           appointments=appointments,
                           result=None)

# ---------------- ADD PATIENT ----------------
@app.route('/add_patient', methods=['POST'])
def add_patient():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("INSERT INTO patients(name, age, disease) VALUES (?, ?, ?)",
                (request.form['name'], request.form['age'], request.form['disease']))

    conn.commit()
    conn.close()
    return redirect('/dashboard')

# ---------------- DELETE PATIENT ----------------
@app.route('/delete_patient/<int:id>')
def delete_patient(id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM patients WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

# ---------------- ADD DOCTOR ----------------
@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("INSERT INTO doctors(name, specialization) VALUES (?, ?)",
                (request.form['dname'], request.form['specialization']))

    conn.commit()
    conn.close()
    return redirect('/dashboard')

# ---------------- DELETE DOCTOR ----------------
@app.route('/delete_doctor/<int:id>')
def delete_doctor(id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM doctors WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

# ---------------- BOOK APPOINTMENT ----------------
@app.route('/book', methods=['POST'])
def book():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("INSERT INTO appointments(patient, doctor, date) VALUES (?, ?, ?)",
                (request.form['patient'], request.form['doctor'], request.form['date']))

    conn.commit()
    conn.close()
    return redirect('/dashboard')

# ---------------- AI RECOMMENDATION ----------------
@app.route('/recommend', methods=['POST'])
def recommend():
    if 'user' not in session:
        return redirect('/')

    symptom = request.form['symptom']
    result = predict_specialization(symptom)

    conn = connect_db()
    cur = conn.cursor()

    patients = cur.execute("SELECT * FROM patients").fetchall()
    doctors = cur.execute("SELECT * FROM doctors").fetchall()
    appointments = cur.execute("SELECT * FROM appointments").fetchall()

    conn.close()

    return render_template('dashboard.html',
                           patients=patients,
                           doctors=doctors,
                           appointments=appointments,
                           result=result)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run()