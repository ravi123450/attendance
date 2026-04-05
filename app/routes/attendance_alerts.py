from flask import Blueprint, jsonify
from datetime import datetime
from sqlalchemy import extract
from app import db
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.notice import Notice

alerts_bp = Blueprint("alerts", __name__)


# ===============================
# CORE LOGIC FUNCTION
# ===============================
def process_attendance_alerts(student_id):

    now = datetime.utcnow()

    # ===============================
    # 1️⃣ CHECK CONSECUTIVE ABSENT
    # ===============================
    last_two = Attendance.query.filter_by(
        student_id=student_id
    ).order_by(Attendance.date.desc()).limit(2).all()

    if len(last_two) == 2:
        if last_two[0].status == "ABSENT" and last_two[1].status == "ABSENT":

            exists = Notice.query.filter_by(
                student_id=student_id,
                message="⚠ You were absent for 2 consecutive days."
            ).first()

            if not exists:
                notice = Notice(
                    student_id=student_id,
                    message="⚠ You were absent for 2 consecutive days.",
                    created=datetime.utcnow(),
                    read=False
                )
                db.session.add(notice)


    # ===============================
    # 2️⃣ CHECK MONTHLY LOW ATTENDANCE
    # ===============================
    monthly_records = Attendance.query.filter(
        Attendance.student_id == student_id,
        extract("month", Attendance.date) == now.month,
        extract("year", Attendance.date) == now.year
    ).all()

    if len(monthly_records) > 0:

        total = len(monthly_records)
        present = len([r for r in monthly_records if r.status == "PRESENT"])

        percent = (present / total) * 100

        if percent < 75:

            msg = f"⚠ Your attendance this month is low ({round(percent)}%). Minimum required is 75%."

            exists = Notice.query.filter_by(
                student_id=student_id,
                message=msg
            ).first()

            if not exists:
                notice = Notice(
                    student_id=student_id,
                    message=msg,
                    created=datetime.utcnow(),
                    read=False
                )
                db.session.add(notice)

    db.session.commit()


# ===============================
# NEW API ENDPOINT
# ===============================
@alerts_bp.route("/system/check-attendance-alerts/<int:student_id>", methods=["POST"])
def check_attendance_alerts(student_id):

    process_attendance_alerts(student_id)

    return jsonify({"message": "Attendance alerts checked successfully"})