import cv2
import face_recognition
import pickle
import os


def capture_and_encode(name, student_id, num_samples=5):
    encodings = []
    cam = cv2.VideoCapture(0)
    count = 0

    while count < num_samples:
        ret, frame = cam.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb)

        if face_locations:
            face_encodings = face_recognition.face_encodings(
                rgb, face_locations)
            encodings.append(face_encodings[0])
            count += 1
            print(f"Captured sample {count}/{num_samples}")

        cv2.imshow('Registering face - press q to quit early', frame)
        if cv2.waitKey(500) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

    if not encodings:
        print("No face was captured. Try again with better lighting.")
        return

    os.makedirs('recognition/encodings', exist_ok=True)
    save_path = f'recognition/encodings/{student_id}.pkl'
    with open(save_path, 'wb') as f:
        pickle.dump({'name': name, 'student_id': student_id,
                    'encodings': encodings}, f)

    print(f"Saved encoding for {name} to {save_path}")


if __name__ == '__main__':
    name = input("Enter student name: ")
    student_id = input("Enter student ID: ")
    capture_and_encode(name, student_id)
