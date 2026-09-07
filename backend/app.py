import os
from flask import Flask, render_template, request
from database.models import db

from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

template_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..', 'frontend', 'templates')
app = Flask(__name__, template_folder=template_dir)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'attendance.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
db.init_app(app)

# Set up Flask-Login in app.py
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'development-only-secret')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'


@login_manager.user_loader
def load_user(user_id):
    from database.models import User
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    from database.models import AttendanceRecord
    records = AttendanceRecord.query.all()
    return render_template('dashboard.html', records=records)


@app.route('/add-student/<name>/<student_id>')
def add_student(name, student_id):
    from database.models import Student
    existing = Student.query.filter_by(student_id=student_id).first()
    if existing:
        return f'{name} is already registered.'
    new_student = Student(name=name, student_id=student_id)
    db.session.add(new_student)
    db.session.commit()
    return f'{name} added with student ID {student_id}!'


@app.route('/register')
def register_page():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register_submit():
    from database.models import Student
    name = request.form['name']
    student_id = request.form['student_id']

    existing = Student.query.filter_by(student_id=student_id).first()
    if existing:
        return f'{student_id} is already registered.'

    new_student = Student(name=name, student_id=student_id)
    db.session.add(new_student)
    db.session.commit()
    return f'{name} registered! Now run register_face.py to capture their face.'


@app.route('/students')
def students_page():
    from database.models import Student
    students = Student.query.all()
    return render_template('students.html', students=students)


@app.route('/start-session')
def start_session():
    import threading
    try:
        from recognition.recognize_face import run_recognition
    except ImportError as exc:
        return f'Face recognition dependencies are unavailable: {exc}', 503

    thread = threading.Thread(target=run_recognition, daemon=True)
    thread.start()

    return 'Session started! Camera is now running in the background.'

# login


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_submit():
    from database.models import User
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        return redirect('/')
    else:
        return render_template('login.html', error='Invalid username or password.')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
