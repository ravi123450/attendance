from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from datetime import date, datetime

from app.extensions import db
from app.models.user import User
from app.models.student import Student
from app.models.attendance import Attendance
from app.services.face_service import recognize_live
from app.utils.time_rules import attendance_open


bp = Blueprint("attendance", __name__, url_prefix="/attendance")


# ==========================
# CORE MARK FUNCTION
# ==========================

def mark(student, teacher_id, method):

    today = date.today()

    exists = Attendance.query.filter_by(
        student_id=student.id,
        day=today     # ✅ correct
    ).first()

    if exists:
        return False


    att = Attendance(
        student_id=student.id,
        teacher_id=teacher_id,
        day=today,     # ✅ correct
        time=datetime.utcnow(),
        method=method
    )

    db.session.add(att)
    db.session.commit()

    return True



# ==========================
# FACE ATTENDANCE
# ==========================
@bp.route("/face", methods=["POST"])
@jwt_required()
def face_attendance():

    uid = get_jwt_identity()
    teacher = User.query.get(uid)


    if teacher.role != "TEACHER":
        return {"error": "Unauthorized"}, 403


    if not attendance_open():
        return {"error": "Closed"}, 403


    img = request.files.get("face")

    students = Student.query.all()


    stu = recognize_live(img, students)


    if not stu:
        return {"status": "NO_MATCH"}


    saved = mark(stu, teacher.id, "FACE")


    if not saved:
        return {"status": "ALREADY"}


    return {
        "status": "SUCCESS",
        "name": stu.name,
        "roll": stu.roll_no,
        "time": datetime.now().strftime("%H:%M:%S")
    }


# ==========================
# QR ATTENDANCE
# ==========================

@bp.route("/qr", methods=["POST"])
@jwt_required()
def qr_attendance():

    uid = get_jwt_identity()

    teacher = User.query.get(uid)


    if teacher.role != "TEACHER":
        return {"error":"Unauthorized"},403


    if not attendance_open():
        return {"error":"Closed"},403


    code = request.json.get("code")


    stu = Student.query.filter_by(qr_code=code).first()


    if not stu:
        return {"status":"INVALID"}


    saved = mark(stu, teacher.id, "QR")


    if not saved:
        return {"status":"ALREADY_MARKED"}


    from datetime import datetime

    return {
        "status": "SUCCESS",
        "name": stu.name,
        "roll": stu.roll_no,
        "time": datetime.now().strftime("%H:%M:%S")
    }

@bp.route("/qr-image", methods=["POST"])
@jwt_required()
def qr_image_attendance():

    uid = get_jwt_identity()
    teacher = User.query.get(uid)

    if teacher.role != "TEACHER":
        return {"error": "Unauthorized"}, 403

    if not attendance_open():
        return {"error": "Closed"}, 403

    img = request.files.get("qr")

    if not img:
        return {"status": "NO_QR"}

    # Decode using OpenCV (no zbar)
    import cv2
    import numpy as np

    data = img.read()
    arr = np.frombuffer(data, np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    detector = cv2.QRCodeDetector()
    code, _, _ = detector.detectAndDecode(frame)

    if not code:
        return {"status": "INVALID"}

    stu = Student.query.filter_by(qr_code=code).first()

    if not stu:
        return {"status": "INVALID"}

    saved = mark(stu, teacher.id, "QR")

    if not saved:
        return {"status": "ALREADY"}

    from datetime import datetime

    return {
        "status": "SUCCESS",
        "name": stu.name,
        "roll": stu.roll_no,
        "time": datetime.now().strftime("%H:%M:%S")
    }
