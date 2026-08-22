from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from prolog.bridge import assert_attendance, assert_class_start, is_late

SESSION_ID = "session1"
CLASS_START_MINUTES = 9 * 60  # 9:00 AM as minutes since midnight

db = SQLAlchemy()


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)


class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='present')

    student = db.relationship('Student')

# save attendance on the database connect with the recognize_face


def mark_attendance(roll_number):
    student = Student.query.filter_by(roll_number=roll_number).first()
    if not student:
        print(f"No student found with roll number {roll_number}")
        return None

    recent_cutoff = datetime.utcnow() - timedelta(minutes=1)
    existing = AttendanceRecord.query.filter(
        AttendanceRecord.student_id == student.id,
        AttendanceRecord.timestamp > recent_cutoff
    ).first()
    if existing:
        return None

    now = datetime.now()
    # converts real time into minuites from the midnight. because the prolog understand just plain numbers
    minutes_since_midnight = now.hour * 60 + now.minute

    assert_class_start(SESSION_ID, CLASS_START_MINUTES)
    assert_attendance(roll_number, SESSION_ID, minutes_since_midnight)

    status = 'late' if is_late(roll_number, SESSION_ID) else 'present'

    record = AttendanceRecord(student_id=student.id, status=status)
    db.session.add(record)
    db.session.commit()
    return record
