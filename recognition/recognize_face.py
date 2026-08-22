from database.models import db, mark_attendance
from flask import Flask
import glob
import pickle
import face_recognition
import cv2
import os


app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'attendance.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
db.init_app(app)


def load_known_faces():
    known = []
    for path in glob.glob('recognition/encodings/*.pkl'):
        with open(path, 'rb') as f:
            data = pickle.load(f)
            for encoding in data['encodings']:
                known.append({
                    'encoding': encoding,
                    'name': data['name'],
                    'roll_number': data['roll_number']
                })
    return known


def run_recognition():
    known_faces = load_known_faces()
    if not known_faces:
        print("No registered faces found. Run register_face.py first.")
        return

    known_encodings = [k['encoding'] for k in known_faces]
    cam = cv2.VideoCapture(0)

    print("Camera started. Press 'q' to quit.")

    with app.app_context():
        while True:
            ret, frame = cam.read()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb)
            face_encodings = face_recognition.face_encodings(
                rgb, face_locations)

            for encoding, location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(
                    known_encodings, encoding, tolerance=0.5)
                name = "Unknown"

                if True in matches:
                    match_index = matches.index(True)
                    matched = known_faces[match_index]
                    name = matched['name']
                    record = mark_attendance(matched['roll_number'])
                    if record:
                        print(f"Marked attendance: {name}")
                    else:
                        print(f"Recognized {name} (already marked recently)")

                top, right, bottom, left = location
                cv2.rectangle(frame, (left, top),
                              (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            cv2.imshow('Recognition - press q to quit', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    run_recognition()
