# Facial Attendance System

## Run the web dashboard

```bash
python3 -m pip install -r requirements.txt
python3 -m backend.app
```

Open <http://127.0.0.1:5000/> in a browser. The SQLite database is created
automatically at `database/attendance.db`.

Face registration and recognition additionally require working OpenCV,
`face_recognition`, a camera, and (for Prolog-backed rules) SWI-Prolog.
The dashboard remains usable without those optional native dependencies and
reports a clear error if a camera session is started without them.