from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from prolog.bridge import assert_attendance, assert_class_start, is_late

db = SQLAlchemy()

SESSION_ID = "session1"
CLASS_START_MINUTES = 9 * 60  # 9:00 AM, as minutes since midnight


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)


class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='present')

    student = db.relationship('Student')


def mark_attendance(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        print(f"No student found with student ID {student_id}")
        return None

    recent_cutoff = datetime.utcnow() - timedelta(minutes=1)
    existing = AttendanceRecord.query.filter(
        AttendanceRecord.student_id == student.id,
        AttendanceRecord.timestamp > recent_cutoff
    ).first()
    if existing:
        return None

    now = datetime.now()
    minutes_since_midnight = now.hour * 60 + now.minute

    assert_class_start(SESSION_ID, CLASS_START_MINUTES)
    assert_attendance(student_id, SESSION_ID, minutes_since_midnight)

    status = 'late' if is_late(student_id, SESSION_ID) else 'present'

    record = AttendanceRecord(student_id=student.id, status=status)
    db.session.add(record)
    db.session.commit()
    return record
