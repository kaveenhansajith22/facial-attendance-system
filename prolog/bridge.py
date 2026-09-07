import os

try:
    from pyswip import Prolog
except ImportError:
    Prolog = None

prolog = None
if Prolog is not None:
    try:
        prolog = Prolog()
        rules_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rules.pl')
        prolog.consult(rules_path)
    except (OSError, RuntimeError):
        # SWI-Prolog is optional for the web dashboard.
        prolog = None

_attendance = set()
_class_starts = {}


def _atom(value):
    """Return a safely quoted Prolog atom."""
    text = str(value)
    return "'" + text.replace("\\", "\\\\").replace("'", "\\'") + "'"


def assert_attendance(student, session, time_value):
    if prolog is not None:
        prolog.assertz(f"attended({_atom(student)}, {_atom(session)}, {int(time_value)})")
    _attendance.add((str(student), str(session), int(time_value)))


def assert_class_start(session, start_time):
    _class_starts[str(session)] = int(start_time)
    if prolog is not None:
        prolog.assertz(f"class_start({_atom(session)}, {int(start_time)})")


def is_late(student, session):
    if prolog is not None:
        result = list(prolog.query(f"late({_atom(student)}, {_atom(session)})"))
        return bool(result)
    start = _class_starts.get(str(session))
    return start is not None and any(
        s == str(student) and session_name == str(session) and time > start + 15
        for s, session_name, time in _attendance
    )


def is_eligible(student, total_sessions):
    if prolog is not None:
        result = list(prolog.query(f"eligible({_atom(student)}, {int(total_sessions)})"))
        return bool(result)
    if total_sessions <= 0:
        return False
    attended = len({session for s, session, _ in _attendance if s == str(student)})
    return (attended / total_sessions) * 100 >= 75
