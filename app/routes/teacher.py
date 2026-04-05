from app.models.attendance import Attendance
from app.models.notice import Notice
from app.models.notice import Notice
from app.models.user import User
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

from app.models.student import Student
from app.extensions import db
from app.services.qr_service import generate_qr
from werkzeug.security import generate_password_hash
from app.services.face_service import get_average_embedding
from app.models.activity import Activity
from app.models.activity_submission import ActivitySubmission




bp = Blueprint("teacher", __name__, url_prefix="/teacher")

@bp.route("/add-student", methods=["POST"])
@jwt_required()
def add_student():
    uid = get_jwt_identity()
    name = request.form.get("name")
    roll = request.form.get("roll_no")
    cls = request.form.get("class_name")
    sec = request.form.get("section")
    teacher = User.query.get(uid)

    email = request.form.get("email")

    school = teacher.school

    faces = request.files.getlist("faces")

    password = "student@123"


    if len(faces) < 5:
        return {"error": "Need more face samples"}, 400


    if Student.query.filter_by(
    roll_no=roll,
    school=teacher.school,
    section=sec
    ).first():

     return {"error": "Student exists in this section"}, 409

        


    emb = get_average_embedding(faces)

    if emb is None:
        return {"error": "Face capture failed"}, 400


    qr_code, qr_path = generate_qr(roll)


    student = Student(
        name=name,
        roll_no=roll,
        class_name=cls,
        section=sec,
        email=email,
        face_embedding=emb,
        qr_code=qr_code,
        qr_image=qr_path,
        school=school, 
    )

    student.set_password(password)

    db.session.add(student)
    db.session.commit()

    return {"msg": "Student enrolled successfully"}

@bp.route("/stats", methods=["GET"])
@jwt_required()
def teacher_stats():

    uid = get_jwt_identity()
    teacher = User.query.get(uid)

    if not teacher or teacher.role != "TEACHER":
        return {"error": "Unauthorized"}, 403

    # ✅ Get students of this teacher's school
    students = Student.query.filter_by(school=teacher.school).all()
    total_students = len(students)

    if total_students == 0:
        return {
            "students": 0,
            "rate": 0,
            "low": 0
        }

    student_ids = [s.id for s in students]

    # ✅ Total attendance entries (only for this school)
    total_attendance = Attendance.query.filter(
        Attendance.student_id.in_(student_ids)
    ).count()

    # ---------------- LOW ATTENDANCE ----------------
    low_attendance = 0

    # 👉 Count total "days" using max records per student
    # (approximation since no absent data)
    max_days = 0

    student_counts = {}

    for s in students:
        count = Attendance.query.filter_by(student_id=s.id).count()
        student_counts[s.id] = count

        if count > max_days:
            max_days = count

    # 👉 Calculate per student %
    for s in students:
        student_total = student_counts[s.id]

        if max_days > 0:
            percent = (student_total / max_days) * 100

            if percent < 70:
                low_attendance += 1

    # ---------------- RATE ----------------
    rate = 0

    if max_days > 0:
        total_possible = total_students * max_days
        rate = round((total_attendance / total_possible) * 100, 1)

    return {
        "students": total_students,
        "rate": rate,
        "low": low_attendance
    }
@bp.route("/reports/csv")
@jwt_required()
def all_reports():

    uid = get_jwt_identity()
    teacher = User.query.get(uid)

    import csv
    from io import StringIO
    from flask import Response

    out = StringIO()
    writer = csv.writer(out)

    writer.writerow(["Name","Roll","Date","Time","Method"])


    rows = db.session.query(
        Student.name,
        Student.roll_no,
        Attendance.day,
        Attendance.time,
        Attendance.method
    ).join(Attendance).filter(
        Student.school==teacher.school
    ).all()


    for r in rows:
        writer.writerow([
            r[0],r[1],r[2],
            r[3].strftime("%H:%M"),
            r[4]
        ])


    resp = Response(out.getvalue(), mimetype="text/csv")
    resp.headers["Content-Disposition"]="attachment;filename=all.csv"

    return resp

@bp.route("/delete-student/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_student(id):

    uid = get_jwt_identity()
    teacher = User.query.get(uid)

    stu = Student.query.get(id)

    if not stu:
        return {"error":"Not found"},404


    # ✅ CHECK SCHOOL
    if stu.school != teacher.school:
        return {"error":"Unauthorized"},403


    Attendance.query.filter_by(student_id=id).delete()

    db.session.delete(stu)
    db.session.commit()

    return {"status":"DELETED"}


@bp.route("/notice", methods=["POST"])
@jwt_required()
def send_notice():

    uid = get_jwt_identity()
    teacher = User.query.get(uid)

    data = request.json

    message = data.get("message")

    if not message:
        return {"msg": "Message required"}, 400


    notice = Notice(
    title="Alert",
    message=message,
    school=teacher.school   # ✅ bind to teacher school
)


    db.session.add(notice)
    db.session.commit()

    return {"msg": "Notice sent successfully"}

# ===========================
# GET ALL STUDENTS
# ===========================
@bp.route("/students", methods=["GET"])
@jwt_required()
def get_students():

    uid = get_jwt_identity()
    teacher = User.query.get(uid)

    if teacher.role != "TEACHER":
        return {"error": "Unauthorized"}, 403

    students = Student.query.filter_by(
        school=teacher.school
    ).all()

    data = []

    for s in students:
        data.append({
            "id": s.id,
            "name": s.name,
            "roll": s.roll_no,
            "class": s.class_name,
            "section": s.section
        })

    return data
@bp.route("/activity", methods=["POST"])
@jwt_required()
def create_activity():

    uid = get_jwt_identity()
    teacher = User.query.get(uid)

    data = request.json

    title = data.get("title")
    desc = data.get("description")


    cls = data.get("class")
    sec = data.get("section")

    if not title or not cls or not sec:
        return {"error":"Missing fields"},400


    activity = Activity(
        title=title,
        description=desc,
        school=teacher.school,
        class_name=cls,
        section=sec,
        created_by=uid
    )
    db.session.add(activity)
    db.session.commit()

    return {"msg":"Activity created"}
@bp.route("/activities")
@jwt_required()
def teacher_activities():

    uid = get_jwt_identity()
    teacher = User.query.get(uid)

    rows = Activity.query.filter_by(
        school=teacher.school,
        created_by=uid
    ).all()

    return [{
        "id":a.id,
        "title":a.title,
        "class":a.class_name,
        "section":a.section,
        "date":a.created_at.strftime("%d %b")
    } for a in rows]



# ================= SUBMISSIONS =================

@bp.route("/activity/<int:id>/submissions")
@jwt_required()
def view_submissions(id):

    rows = ActivitySubmission.query.filter_by(
        activity_id=id
    ).all()

    data = []

    for s in rows:

        stu = Student.query.get(s.student_id)

        data.append({
            "id": s.id,
            "name": stu.name,        # ✅
            "roll": stu.roll_no,     # ✅
            "photo": s.photo,
            "status": s.status,
            "activity_id": id
        })

    return data



# ================= VERIFY =================

@bp.route("/submission/<int:id>/status", methods=["PUT"])
@jwt_required()
def update_submission(id):

    data = request.json

    status = data.get("status")

    if status not in ["APPROVED", "REJECTED"]:
        return {"error":"Invalid status"},400


    sub = ActivitySubmission.query.get(id)

    if not sub:
        return {"error":"Not found"},404


    sub.status = status
    db.session.commit()

    return {"msg":"Updated"}

@bp.route("/activity/history")
@jwt_required()
def activity_history():

    sid = get_jwt_identity()

    rows = ActivitySubmission.query.filter_by(
        student_id=sid
    ).all()

    data = []

    for r in rows:

        act = Activity.query.get(r.activity_id)

        data.append({
            "title":act.title,
            "status":r.status,
            "date":r.submitted_at.strftime("%d %b")
        })

    return data

from flask import request



@bp.route("/reset-student-password", methods=["POST"])
@jwt_required()
def reset_student_password():

    uid = get_jwt_identity()
    user = User.query.get(uid)

    # ✅ Authorization
    if not user or user.role not in ["ADMIN", "TEACHER"]:
        return {"error": "Unauthorized"}, 403

    data = request.get_json()

    if not data:
        return {"error": "Invalid JSON"}, 400

    roll_no = data.get("roll_no")
    class_name = data.get("class_name")
    section = data.get("section")

    # ✅ Validate input
    if not roll_no or not class_name or not section:
        return {"error": "roll_no, class_name and section are required"}, 400

    # ✅ IMPORTANT: use teacher's school
    school = user.school

    # ✅ Find student using UNIQUE constraint fields
    student = Student.query.filter_by(
        roll_no=roll_no,
        school=school,
        class_name=class_name,
        section=section
    ).first()

    if not student:
        return {"error": "Student not found"}, 404

    # ✅ Reset password
    student.set_password("Student@123")

    db.session.commit()

    return {
        "message": f"Password reset successful for {student.name}",
    }