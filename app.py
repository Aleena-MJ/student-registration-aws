from dotenv import load_dotenv
load_dotenv()
import os
import re
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, abort

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'student-registration-secret-key-ec2-ready')

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "3306")),
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"]
    )

def init_db():
    """Create the students table in MySQL if it does not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(100) UNIQUE NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone VARCHAR(30) NOT NULL,
            dob VARCHAR(20) NOT NULL,
            gender VARCHAR(50) NOT NULL,
            course VARCHAR(100) NOT NULL,
            year VARCHAR(50) NOT NULL,
            address TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Initialize database automatically when the app module is loaded
init_db()


def validate_student_data(data, student_db_id=None):
    """
    Validate student form input fields.
    Returns a list of error messages (empty if all valid).
    """
    errors = []
    
    student_id = data.get('student_id', '').strip()
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    dob = data.get('dob', '').strip()
    gender = data.get('gender', '').strip()
    course = data.get('course', '').strip()
    year = data.get('year', '').strip()
    address = data.get('address', '').strip()

    # Check for empty required fields
    if not student_id:
        errors.append("Student ID is required.")
    if not full_name:
        errors.append("Full Name is required.")
    if not email:
        errors.append("Email address is required.")
    if not phone:
        errors.append("Phone Number is required.")
    if not dob:
        errors.append("Date of Birth is required.")
    if not gender:
        errors.append("Gender is required.")
    if not course:
        errors.append("Course is required.")
    if not year:
        errors.append("Year of study is required.")
    if not address:
        errors.append("Address is required.")

    # Email format validation
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if email and not re.match(email_regex, email):
        errors.append("Please provide a valid email address.")

    # Phone number format validation (basic check for digits/spaces/dashes/plus)
    phone_clean = re.sub(r'[\s\-\(\)\+]', '', phone)
    if phone and (not phone_clean.isdigit() or len(phone_clean) < 7 or len(phone_clean) > 15):
        errors.append("Please provide a valid phone number (7 to 15 digits).")

    # Database uniqueness validation
    if student_id or email:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check duplicate Student ID
        if student_id:
            if student_db_id:
                cursor.execute(
                    "SELECT id FROM students WHERE LOWER(student_id) = LOWER(%s) AND id != %s",
                    (student_id, student_db_id)
                )
            else:
                cursor.execute(
                    "SELECT id FROM students WHERE LOWER(student_id) = LOWER(%s)",
                    (student_id,)
                )
            if cursor.fetchone():
                errors.append(f"Student ID '{student_id}' is already registered to another student.")

        # Check duplicate Email
        if email:
            if student_db_id:
                cursor.execute(
                    "SELECT id FROM students WHERE LOWER(email) = LOWER(%s) AND id != %s",
                    (email, student_db_id)
                )
            else:
                cursor.execute(
                    "SELECT id FROM students WHERE LOWER(email) = LOWER(%s)",
                    (email,)
                )
            if cursor.fetchone():
                errors.append(f"Email '{email}' is already registered to another student.")

        conn.close()

    return errors


@app.route('/')
def index():
    """Home / Dashboard page displaying summary statistics and recent registrations."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Total students count
    cursor.execute("SELECT COUNT(*) AS total FROM students")
    total_students = cursor.fetchone()['total']

    # Total unique courses
    cursor.execute("SELECT COUNT(DISTINCT course) AS total_courses FROM students")
    total_courses = cursor.fetchone()['total_courses']

    # Recent 5 registrations
    cursor.execute("SELECT * FROM students ORDER BY id DESC LIMIT 5")
    recent_students = cursor.fetchall()

    conn.close()
    return render_template(
        'index.html',
        total_students=total_students,
        total_courses=total_courses,
        recent_students=recent_students
    )


@app.route('/students')
def students():
    """Display list of all registered students with optional search filtering."""
    query = request.args.get('q', '').strip()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if query:
        search_pattern = f"%{query}%"
        cursor.execute(
            """
            SELECT * FROM students
            WHERE student_id LIKE %s OR full_name LIKE %s OR email LIKE %s
            ORDER BY id DESC
            """,
            (search_pattern, search_pattern, search_pattern)
        )
    else:
        cursor.execute("SELECT * FROM students ORDER BY id DESC")

    all_students = cursor.fetchall()
    conn.close()

    return render_template('students.html', students=all_students, query=query)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new student."""
    if request.method == 'POST':
        form_data = {
            'student_id': request.form.get('student_id', '').strip(),
            'full_name': request.form.get('full_name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'dob': request.form.get('dob', '').strip(),
            'gender': request.form.get('gender', '').strip(),
            'course': request.form.get('course', '').strip(),
            'year': request.form.get('year', '').strip(),
            'address': request.form.get('address', '').strip(),
        }

        errors = validate_student_data(form_data)

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html', student=form_data)

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                INSERT INTO students (
                    student_id, full_name, email, phone, dob, gender, course, year, address
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    form_data['student_id'],
                    form_data['full_name'],
                    form_data['email'],
                    form_data['phone'],
                    form_data['dob'],
                    form_data['gender'],
                    form_data['course'],
                    form_data['year'],
                    form_data['address']
                )
            )
            conn.commit()
            conn.close()

            flash(f"Student '{form_data['full_name']}' registered successfully!", 'success')
            return redirect(url_for('students'))
        except mysql.connector.IntegrityError:
            flash("Database error: A record with this Student ID or Email already exists.", 'danger')
            return render_template('register.html', student=form_data)
        except Exception as e:
            flash(f"An unexpected error occurred while saving the record.", 'danger')
            return render_template('register.html', student=form_data)

    return render_template('register.html', student={})


@app.route('/students/<int:id>')
def student_details(id):
    """View complete details of a single student."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE id = %s", (id,))
    student = cursor.fetchone()
    conn.close()

    if student is None:
        flash("Student record not found.", 'warning')
        return redirect(url_for('students'))

    return render_template('student_details.html', student=student)


@app.route('/students/<int:id>/edit', methods=['GET', 'POST'])
def edit_student(id):
    """Edit an existing student record."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE id = %s", (id,))
    student = cursor.fetchone()

    if student is None:
        conn.close()
        flash("Student record not found.", 'warning')
        return redirect(url_for('students'))

    if request.method == 'POST':
        form_data = {
            'student_id': request.form.get('student_id', '').strip(),
            'full_name': request.form.get('full_name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'dob': request.form.get('dob', '').strip(),
            'gender': request.form.get('gender', '').strip(),
            'course': request.form.get('course', '').strip(),
            'year': request.form.get('year', '').strip(),
            'address': request.form.get('address', '').strip(),
        }

        errors = validate_student_data(form_data, student_db_id=id)

        if errors:
            conn.close()
            for error in errors:
                flash(error, 'danger')
            # Pass form_data back with the id so the form action URL remains valid
            form_data['id'] = id
            return render_template('edit_student.html', student=form_data)

        try:
            cursor.execute(
                """
                UPDATE students SET
                    student_id = %s,
                    full_name = %s,
                    email = %s,
                    phone = %s,
                    dob = %s,
                    gender = %s,
                    course = %s,
                    year = %s,
                    address = %s
                WHERE id = %s
                """,
                (
                    form_data['student_id'],
                    form_data['full_name'],
                    form_data['email'],
                    form_data['phone'],
                    form_data['dob'],
                    form_data['gender'],
                    form_data['course'],
                    form_data['year'],
                    form_data['address'],
                    id
                )
            )
            conn.commit()
            conn.close()

            flash(f"Student details for '{form_data['full_name']}' updated successfully!", 'success')
            return redirect(url_for('student_details', id=id))
        except mysql.connector.IntegrityError:
            conn.close()
            flash("Database error: Another student with this Student ID or Email already exists.", 'danger')
            form_data['id'] = id
            return render_template('edit_student.html', student=form_data)
        except Exception as e:
            conn.close()
            flash("An unexpected error occurred while updating the record.", 'danger')
            form_data['id'] = id
            return render_template('edit_student.html', student=form_data)

    conn.close()
    return render_template('edit_student.html', student=student)


@app.route('/students/<int:id>/delete', methods=['POST'])
def delete_student(id):
    """Delete a student record."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT full_name FROM students WHERE id = %s", (id,))
    student = cursor.fetchone()

    if student is None:
        conn.close()
        flash("Student record not found or already deleted.", 'warning')
        return redirect(url_for('students'))

    student_name = student['full_name']
    cursor.execute("DELETE FROM students WHERE id = %s", (id,))
    conn.commit()
    conn.close()

    flash(f"Student '{student_name}' was successfully deleted.", 'success')
    return redirect(url_for('students'))


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors gracefully."""
    return render_template('base.html', not_found=True), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors gracefully."""
    return render_template('base.html', server_error=True), 500


if __name__ == '__main__':
    # Configuration suitable for local testing and AWS EC2 deployment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1')

    print(f"Starting Student Registration App on http://{host}:{port} (Debug: {debug})")
    app.run(host=host, port=port, debug=debug)
