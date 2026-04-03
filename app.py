from flask import Flask, render_template, Response, jsonify, request, redirect, url_for, session
import cv2
import sqlite3
import threading
import time
import atexit
import signal
import sys
import os
import re
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "classroom_monitoring_secret_key_2024"  # For sessions

DB_NAME = "classroom.db"
PORT = int(os.getenv("PORT", 5000))

# Hardcoded admin user for simplicity
ADMIN_USER = "admin"
ADMIN_PASSWORD = "admin123"

# ========== AUTHENTICATION DECORATOR ==========
def login_required(f):
    """Decorator to protect routes that require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ========== CAMERA INITIALIZATION (WITH FALLBACK) ==========
def init_camera():
    """Initialize camera with fallback support for Windows."""
    for index in [0, 1]:
        try:
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if cap.isOpened():
                print(f"✓ Camera initialized on index {index}")
                return cap
            cap.release()
        except Exception as e:
            print(f"✗ Camera index {index} failed: {e}")
    
    print("✗ No camera available - running in simulation mode")
    return None


camera = init_camera()

# ========== HAAR CASCADE CLASSIFIERS ==========
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye.xml"
)

# ========== THREAD SAFETY & SHARED VARIABLES ==========
lock = threading.Lock()
latest_frame = None
latest_score = 0.0
latest_status = "Starting..."
latest_faces = 0
latest_engaged = 0
last_saved_time = 0
running = True  # Flag to control thread shutdown


# ========== RESOURCE CLEANUP ==========
def cleanup():
    """Release camera and cleanup resources."""
    global camera, running
    
    running = False
    if camera is not None:
        try:
            camera.release()
            print("✓ Camera released successfully")
        except Exception as e:
            print(f"✗ Error releasing camera: {e}")
    cv2.destroyAllWindows()


# Register cleanup on exit
atexit.register(cleanup)

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n✓ Shutting down...")
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ========== DATABASE OPERATIONS ==========
def init_db():
    """Create tables if they do not exist and add sample data."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_no TEXT UNIQUE,
                attendance TEXT DEFAULT 'Present'
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS engagement_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                score REAL NOT NULL,
                faces_detected INTEGER NOT NULL,
                engaged_faces INTEGER NOT NULL,
                status TEXT NOT NULL
            )
        """)

        conn.commit()

        # Add sample students only if table is empty
        cur.execute("SELECT COUNT(*) FROM students")
        count = cur.fetchone()[0]
        if count == 0:
            sample_students = [
                ("Student 1", "CSE01"),
                ("Student 2", "CSE02"),
                ("Student 3", "CSE03")
            ]
            for name, roll_no in sample_students:
                cur.execute(
                    "INSERT OR IGNORE INTO students (name, roll_no) VALUES (?, ?)",
                    (name, roll_no)
                )
            conn.commit()

        conn.close()
        print("✓ Database initialized")

    except Exception as e:
        print(f"✗ Database initialization error: {e}")


def save_log(score, faces, engaged, status):
    """Save current engagement data into database with error handling."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO engagement_logs (timestamp, score, faces_detected, engaged_faces, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            round(score, 2),
            faces,
            engaged,
            status
        ))

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"✗ Error saving log: {e}")


# ========== INPUT VALIDATION ==========
def validate_student_name(name):
    """Validate student name (non-empty, reasonable length)."""
    if not name or len(name.strip()) == 0:
        return False, "Name cannot be empty"
    if len(name) > 100:
        return False, "Name too long (max 100 characters)"
    return True, "Valid"


def validate_roll_no(roll_no):
    """Validate roll number (alphanumeric only, optional field)."""
    if not roll_no or len(roll_no.strip()) == 0:
        return True, "Valid"  # Roll number is optional
    if len(roll_no) > 20:
        return False, "Roll number too long (max 20 characters)"
    if not re.match(r"^[a-zA-Z0-9]+$", roll_no):
        return False, "Roll number must be alphanumeric"
    return True, "Valid"

# ========== AI FRAME PROCESSING ==========
def process_frame(frame):
    """
    Detect faces and eyes, then compute engagement score.
    Engagement = percentage of detected faces with at least one eye detected.
    """
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        total_faces = len(faces)
        engaged_count = 0

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y + h, x:x + w]
            eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=5)

            engaged = len(eyes) >= 1
            if engaged:
                engaged_count += 1
                color = (0, 255, 0)
                label = "Engaged"
            else:
                color = (0, 0, 255)
                label = "Not Engaged"

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(frame, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (255, 0, 0), 1)

        score = (engaged_count / total_faces * 100) if total_faces > 0 else 0.0
        status = "No face detected" if total_faces == 0 else f"{engaged_count}/{total_faces} faces engaged"

        cv2.putText(frame, f"Class Engagement: {score:.1f}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(frame, status, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        return frame, score, total_faces, engaged_count, status

    except Exception as e:
        print(f"✗ Frame processing error: {e}")
        return frame, 0.0, 0, 0, "Processing error"

# ========== BACKGROUND CAMERA WORKER THREAD ==========
def camera_worker():
    """Background thread that continuously reads webcam frames."""
    global latest_frame, latest_score, latest_status, latest_faces, latest_engaged, last_saved_time, running

    if camera is None:
        print("✗ No camera available - worker thread idle")
        return

    last_saved_time = time.time()

    while running:
        try:
            success, frame = camera.read()
            if not success:
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)
            processed, score, faces, engaged, status = process_frame(frame)

            with lock:
                latest_frame = processed.copy()
                latest_score = score
                latest_status = status
                latest_faces = faces
                latest_engaged = engaged

            # Save log every 5 seconds
            now = time.time()
            if now - last_saved_time >= 5:
                save_log(score, faces, engaged, status)
                last_saved_time = now

            time.sleep(0.03)

        except Exception as e:
            print(f"✗ Camera worker error: {e}")
            time.sleep(1)


# ========== VIDEO STREAM GENERATOR ==========
def gen_frames():
    """Stream processed frames to browser."""
    global latest_frame

    while running:
        try:
            with lock:
                frame = None if latest_frame is None else latest_frame.copy()

            if frame is None:
                time.sleep(0.1)
                continue

            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret:
                continue

            frame_bytes = buffer.tobytes()

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )

        except Exception as e:
            print(f"✗ Frame streaming error: {e}")
            time.sleep(0.5)

# ========== FLASK ROUTES ==========

# ========== AUTHENTICATION ROUTES ==========
@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle login page and authentication."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == ADMIN_USER and password == ADMIN_PASSWORD:
            session["user"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Handle logout."""
    session.pop("user", None)
    return redirect(url_for("login"))


# ========== PROTECTED ROUTES ==========
@app.route("/")
@login_required
def index():
    """Serve the main dashboard."""
    return render_template("index.html")


@app.route("/video_feed")
@login_required
def video_feed():
    """Stream video feed to browser."""
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/stats")
@login_required
def api_stats():
    """Return current statistics and recent data."""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        students = cur.execute("""
            SELECT id, name, roll_no, attendance
            FROM students
            ORDER BY id
        """).fetchall()

        logs = cur.execute("""
            SELECT timestamp, score, faces_detected, engaged_faces, status
            FROM engagement_logs
            ORDER BY id DESC
            LIMIT 5
        """).fetchall()

        conn.close()

        return jsonify({
            "score": round(latest_score, 2),
            "status": latest_status,
            "faces": latest_faces,
            "engaged": latest_engaged,
            "students": [dict(row) for row in students],
            "logs": [dict(row) for row in logs]
        })

    except Exception as e:
        print(f"✗ API stats error: {e}")
        return jsonify({
            "error": "Failed to fetch stats",
            "score": 0,
            "status": "Error",
            "faces": 0,
            "engaged": 0,
            "students": [],
            "logs": []
        }), 500


@app.route("/api/add_student", methods=["POST"])
@login_required
def add_student():
    """Add a new student to the database."""
    try:
        data = request.get_json() or {}
        name = data.get("name", "").strip()
        roll_no = data.get("roll_no", "").strip()

        # Validate inputs
        valid_name, name_msg = validate_student_name(name)
        if not valid_name:
            return jsonify({"ok": False, "message": name_msg}), 400

        valid_roll, roll_msg = validate_roll_no(roll_no)
        if not valid_roll:
            return jsonify({"ok": False, "message": roll_msg}), 400

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO students (name, roll_no) VALUES (?, ?)",
            (name, roll_no if roll_no else None)
        )
        conn.commit()
        conn.close()

        return jsonify({"ok": True, "message": "Student added successfully"})

    except sqlite3.IntegrityError:
        return jsonify({"ok": False, "message": "Roll number already exists"}), 400
    except Exception as e:
        print(f"✗ Add student error: {e}")
        return jsonify({"ok": False, "message": "Database error"}), 500


@app.route("/api/chart-data")
@login_required
def chart_data():
    """Return engagement history data for chart visualization."""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Get last 20 engagement logs
        logs = cur.execute("""
            SELECT timestamp, score
            FROM engagement_logs
            ORDER BY id DESC
            LIMIT 20
        """).fetchall()

        conn.close()

        # Reverse to show chronological order (oldest to newest)
        logs = list(reversed([dict(row) for row in logs]))

        timestamps = [log["timestamp"] for log in logs]
        scores = [log["score"] for log in logs]

        return jsonify({
            "ok": True,
            "labels": timestamps,
            "data": scores
        })

    except Exception as e:
        print(f"✗ Chart data error: {e}")
        return jsonify({
            "ok": False,
            "error": "Failed to fetch chart data",
            "labels": [],
            "data": []
        }), 500

# ========== MAIN ==========
if __name__ == "__main__":
    print("=" * 60)
    print("AI-Based Classroom Monitoring System")
    print("=" * 60)

    init_db()

    # Start camera thread only if camera is available
    if camera is not None:
        worker = threading.Thread(target=camera_worker, daemon=True)
        worker.start()
        print("✓ Camera worker thread started")
    else:
        print("⚠ Running without camera (simulation mode)")

    print(f"✓ Starting Flask app on http://localhost:{PORT}")
    print("✓ Press Ctrl+C to shutdown\n")

    try:
        app.run(host="0.0.0.0", port=PORT, debug=False)
    except Exception as e:
        print(f"✗ Flask error: {e}")
        cleanup()