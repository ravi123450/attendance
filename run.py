import os
from app import create_app
from flask import send_from_directory

app = create_app()

# ✅ Absolute base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ✅ Upload folders (safe for production)
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
STUDENT_FOLDER = os.path.join(UPLOAD_FOLDER, "students")
QR_FOLDER = os.path.join(UPLOAD_FOLDER, "qr")

os.makedirs(STUDENT_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

# ✅ Serve uploads folder
app.static_folder = UPLOAD_FOLDER
app.static_url_path = "/uploads"

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ❌ REMOVE debug=True for production
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
import os
from app import create_app
from flask import send_from_directory

app = create_app()

# ✅ Absolute base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ✅ Upload folders (safe for production)
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
STUDENT_FOLDER = os.path.join(UPLOAD_FOLDER, "students")
QR_FOLDER = os.path.join(UPLOAD_FOLDER, "qr")

os.makedirs(STUDENT_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

# ✅ Serve uploads folder
app.static_folder = UPLOAD_FOLDER
app.static_url_path = "/uploads"

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ❌ REMOVE debug=True for production
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port)
