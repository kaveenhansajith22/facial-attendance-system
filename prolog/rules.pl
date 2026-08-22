late(Student, Session) :-
    attended(Student, Session, Time),
    class_start(Session, Start),
    Time > Start + 15.

attendance_count(Student, Count) :-
    aggregate_all(count, attended(Student, _, _), Count).

eligible(Student, TotalSessions) :-
    attendance_count(Student, Attended),
    Percentage is (Attended / TotalSessions) * 100,
    Percentage >= 75.