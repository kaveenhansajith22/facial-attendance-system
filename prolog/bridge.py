from pyswip import Prolog
import os

prolog = Prolog()
rules_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'rules.pl')
prolog.consult(rules_path)


def assert_attendance(student, session, time_value):
    prolog.assertz(f"attended({student}, {session}, {time_value})")


def assert_class_start(session, start_time):
    prolog.assertz(f"class_start({session}, {start_time})")


def is_late(student, session):
    result = list(prolog.query(f"late({student}, {session})"))
    return len(result) > 0


def is_eligible(student, total_sessions):
    result = list(prolog.query(f"eligible({student}, {total_sessions})"))
    return len(result) > 0
