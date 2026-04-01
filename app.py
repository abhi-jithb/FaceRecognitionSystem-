from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import sys
from src.database import DatabaseManager
from src.attendance_manager import AttendanceManager
from src.detector import FaceDetector
from src.encoder import FaceEncoder
from src.capture import FaceCapturer

app = Flask(__name__)
app.secret_key = "secret_key_for_demo"

# Initialize Managers
db = DatabaseManager()
attend_manager = AttendanceManager(db)
encoder = FaceEncoder(db)
capturer = FaceCapturer()
detector = FaceDetector(encoder, attend_manager)

# --- Middleware ---
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Unauthorized Access")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.verify_user(username, password)
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'faculty':
        return redirect(url_for('faculty_dashboard'))
    elif role == 'student':
        return redirect(url_for('student_dashboard'))
    return "Error: Unknown Role"

# --- Admin Views ---

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    faculties = db.get_users_by_role('faculty')
    students = db.get_users_by_role('student')
    courses = db.get_all_courses()
    return render_template('admin.html', faculties=faculties, students=students, courses=courses)

@app.route('/admin/create_faculty', methods=['POST'])
@login_required
@admin_required
def create_faculty():
    username = request.form.get('username')
    password = request.form.get('password')
    if db.create_user(username, password, 'faculty'):
        flash(f"Faculty {username} created")
    else:
        flash("Error creating faculty (username might exist)")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/create_student', methods=['POST'])
@login_required
@admin_required
def create_student():
    username = request.form.get('username')
    password = request.form.get('password')
    if db.create_user(username, password, 'student'):
        flash(f"Student {username} created")
    else:
        flash("Error creating student")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/create_course', methods=['POST'])
@login_required
@admin_required
def create_course():
    name = request.form.get('course_name')
    faculty_id = request.form.get('faculty_id')
    db.create_course(name, faculty_id)
    flash(f"Course {name} created")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/enroll', methods=['POST'])
@login_required
@admin_required
def enroll_student():
    student_id = request.form.get('student_id')
    course_id = request.form.get('course_id')
    db.enroll_student(student_id, course_id)
    flash("Enrolled student")
    return redirect(url_for('admin_dashboard'))

# --- Faculty Views ---

@app.route('/faculty')
@login_required
def faculty_dashboard():
    if session.get('role') != 'faculty':
        return redirect(url_for('dashboard'))
    courses = db.get_courses_by_faculty(session['user_id'])
    return render_template('faculty.html', courses=courses)

@app.route('/faculty/start_attendance/<int:course_id>')
@login_required
def start_attendance(course_id):
    if session.get('role') != 'faculty':
        return redirect(url_for('dashboard'))
    
    # Check if course belongs to faculty (simple check)
    # For demo, we just proceed
    flash(f"Starting attendance for course ID {course_id}. Close the camera window (press 'q') to finish.")
    
    # This will block the response until the window is closed
    detector.start_recognition(course_id=course_id)
    
    return redirect(url_for('faculty_dashboard'))

@app.route('/faculty/register_student', methods=['GET', 'POST'])
@login_required
def register_student():
    if session.get('role') != 'faculty':
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        # Trigger capture
        success = capturer.capture_faces(student_name)
        if success:
            # Trigger encoding
            encoded = encoder.generate_encodings_for_user(student_name)
            if encoded:
                flash(f"Successfully registered {student_name}")
            else:
                flash("Captured but failed to encode")
        else:
            flash("Capture failed")
        return redirect(url_for('faculty_dashboard'))
        
    # List of students not yet registered? (Optional)
    students = db.get_users_by_role('student')
    return render_template('register_student.html', students=students)

# --- Student Views ---

@app.route('/student')
@login_required
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('dashboard'))
    records = db.get_attendance_report(student_name=session['username'])
    return render_template('student.html', records=records)

@app.route('/reports')
@login_required
def reports():
    # Admin can see all, faculty see their courses
    role = session.get('role')
    if role == 'admin':
        records = db.get_attendance_report()
    elif role == 'faculty':
        # Faculty can only see records for their assigned courses
        records = db.get_attendance_report(faculty_id=session['user_id'])
    else:
        # Students should use their own dashboard
        return redirect(url_for('dashboard'))
        
    return render_template('reports.html', records=records)

if __name__ == '__main__':
    # Threaded=False to avoid issues with OpenCV camera on some systems
    app.run(host='0.0.0.0', port=5000, debug=True)
