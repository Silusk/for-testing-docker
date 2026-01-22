from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb
from datetime import date

app = Flask(__name__)
app.secret_key = "secret123"

# ✅ MySQL Configuration
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'        # change if different
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'hospital_db'

mysql = MySQL(app)

# ✅ Function for Direct DB Connection (for advanced queries)
def get_db_connection():
    return MySQLdb.connect(
        host="db",
        user="root",
        passwd="root",
        db="hospital_db"
    )

# 🏠 Home Page
@app.route('/')
def home():
    return render_template('index.html')

# 🔑 Admin Login Validation
@app.route('/admin_login', methods=['POST'])
def admin_login():
    username = request.form['username']
    password = request.form['password']

    # Hardcoded Admin Login
    if username == "admin" and password == "admin123":
        flash("Welcome, Admin!", "success")
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid username or password!", "error")
        return redirect(url_for('home'))

# 🖥️ Dashboard Page
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# 👨‍⚕️ Create New User
@app.route('/create_user', methods=['POST'])
def create_user():
    name = request.form['name']
    role = request.form['role'].lower()
    department = request.form['department']
    email = request.form['email']

    cur = mysql.connection.cursor()

    if role == 'doctor':
        cur.execute("INSERT INTO doctors (name, department, email) VALUES (%s, %s, %s)",
                    (name, department, email))
    elif role == 'nurse':
        cur.execute("INSERT INTO nurses (name, department, email) VALUES (%s, %s, %s)",
                    (name, department, email))
    elif role == 'worker':
        cur.execute("INSERT INTO workers (name, role, department, email) VALUES (%s, %s, %s, %s)",
                    (name, role, department, email))
    else:
        cur.close()
        flash("Invalid role!", "error")
        return redirect(url_for('dashboard'))

    mysql.connection.commit()
    cur.close()
    flash(f"{role.capitalize()} '{name}' added successfully!", "success")
    return redirect(url_for('dashboard'))

# 📋 View All Users by Role
@app.route('/all_users/<role>')
def all_users(role):
    cur = mysql.connection.cursor()

    # Choose the correct table
    if role == 'doctor':
        cur.execute("SELECT * FROM doctors")
    elif role == 'nurse':
        cur.execute("SELECT * FROM nurses")
    elif role == 'worker':
        cur.execute("SELECT * FROM workers")
    else:
        flash("Invalid role!", "error")
        return redirect(url_for('dashboard'))

    data = cur.fetchall()
    cur.close()
    return render_template('all_users.html', users=data, role=role.capitalize())

# 💰 Salary Details
@app.route("/salary/<role>")
def salary_details(role):
    conn = get_db_connection()
    cursor = conn.cursor()

    if role == "doctor":
        cursor.execute("""
            SELECT d.id, d.name, s.salary, s.month, s.status
            FROM doctors d
            LEFT JOIN doctor_salaries s ON d.id = s.doctor_id
        """)
    elif role == "nurse":
        cursor.execute("""
            SELECT n.id, n.name, s.salary, s.month, s.status
            FROM nurses n
            LEFT JOIN nurse_salaries s ON n.id = s.nurse_id
        """)
    elif role == "worker":
        cursor.execute("""
            SELECT w.id, w.name, s.salary, s.month, s.status
            FROM workers w
            LEFT JOIN worker_salaries s ON w.id = s.worker_id
        """)
    else:
        flash("Invalid role!", "error")
        return redirect(url_for('dashboard'))

    users = cursor.fetchall()
    conn.close()
    return render_template("salary.html", users=users, role=role.capitalize())

# 💵 Update Salary
@app.route("/update_salary/<role>", methods=["POST"])
def update_salary(role):
    conn = get_db_connection()
    cursor = conn.cursor()

    if role == "Doctor":
        salary_table, id_col = "doctor_salaries", "doctor_id"
        main_table = "doctors"
    elif role == "Nurse":
        salary_table, id_col = "nurse_salaries", "nurse_id"
        main_table = "nurses"
    else:
        salary_table, id_col = "worker_salaries", "worker_id"
        main_table = "workers"

    cursor.execute(f"SELECT id FROM {main_table}")
    user_ids = [row[0] for row in cursor.fetchall()]

    for uid in user_ids:
        salary = request.form.get(f"salary_{uid}")
        month = request.form.get(f"month_{uid}")
        status = request.form.get(f"status_{uid}")

        if salary and month and status:
            cursor.execute(f"""
                INSERT INTO {salary_table} ({id_col}, salary, month, status)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    salary=VALUES(salary),
                    month=VALUES(month),
                    status=VALUES(status)
            """, (uid, salary, month, status))

    conn.commit()
    conn.close()

    flash(f"{role} salary details updated successfully!", "success")
    return redirect(url_for("salary_details", role=role.lower()))

# ❌ Delete Employee
@app.route("/delete_employee", methods=["GET", "POST"])
def delete_employee():
    if request.method == "POST":
        role = request.form.get("role")
        name = request.form.get("name")
        department = request.form.get("department")
        email = request.form.get("email")

        if role not in ["doctor", "nurse", "worker"]:
            flash("Invalid role selected!", "danger")
            return redirect(url_for("delete_employee"))

        conn = get_db_connection()
        cursor = conn.cursor()

        table_map = {
            "doctor": "doctors",
            "nurse": "nurses",
            "worker": "workers"
        }
        salary_table_map = {
            "doctor": "doctor_salaries",
            "nurse": "nurse_salaries",
            "worker": "worker_salaries"
        }

        main_table = table_map[role]
        salary_table = salary_table_map[role]
        id_col = f"{role}_id"

        # Find employee
        cursor.execute(f"""
            SELECT id FROM {main_table} 
            WHERE name=%s AND department=%s AND email=%s
        """, (name, department, email))
        result = cursor.fetchone()

        if not result:
            flash(f"{role.capitalize()} not found!", "warning")
            conn.close()
            return redirect(url_for("delete_employee"))

        user_id = result[0]

        # Delete salary and employee
        cursor.execute(f"DELETE FROM {salary_table} WHERE {id_col}=%s", (user_id,))
        cursor.execute(f"DELETE FROM {main_table} WHERE id=%s", (user_id,))
        conn.commit()
        conn.close()

        flash(f"{role.capitalize()} '{name}' deleted successfully!", "success")
        return redirect(url_for("delete_employee"))

    return render_template("delete_employee.html")

# 🧍 View Patients
@app.route("/view_patients", methods=["GET", "POST"])
def view_patients():
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM patients WHERE 1=1"
    params = []

    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        father_name = request.form.get("father_name")
        village = request.form.get("village")
        phone = request.form.get("phone")

        if name:
            query += " AND name LIKE %s"
            params.append(f"%{name}%")
        if age:
            query += " AND age = %s"
            params.append(age)
        if father_name:
            query += " AND father_name LIKE %s"
            params.append(f"%{father_name}%")
        if village:
            query += " AND village LIKE %s"
            params.append(f"%{village}%")
        if phone:
            query += " AND phone LIKE %s"
            params.append(f"%{phone}%")

    query += " ORDER BY id DESC"
    cursor.execute(query, tuple(params))
    patients = cursor.fetchall()
    conn.close()

    return render_template("view_patients.html", patients=patients)

# ➕ Add Patient
@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        father_name = request.form.get("father_name")
        village = request.form.get("village")
        phone = request.form.get("phone")
        record_date = date.today()

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO patients (name, age, father_name, village, phone, record_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, age, father_name, village, phone, record_date))
            conn.commit()
            flash(f"Patient '{name}' added successfully!", "success")
        except MySQLdb.IntegrityError:
            flash(f"Patient '{name}' already exists for today.", "warning")

        conn.close()
        return redirect(url_for("add_patient"))

    return render_template("add_patient.html", current_date=date.today())

# 🚀 Run App
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)
