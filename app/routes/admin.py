from datetime import datetime
from app.models.student import Student
from app.models.attendance import Attendance
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User
from app.extensions import db

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/add-teacher", methods=["POST"])
@jwt_required()
def add_teacher():

    user_id = get_jwt_identity()

    admin = User.query.get(int(user_id))

    if not admin or admin.role != "ADMIN":
        return {"error": "Unauthorized"}, 403

    data = request.get_json()

    if not data:
        return {"error": "No data"}, 400

    if User.query.filter_by(email=data["email"]).first():
        return {"error": "Email exists"}, 409
    
    if not data.get("school") or not data.get("subject"):
        return {"error": "School & Subject required"}, 400

    teacher = User(
        name=data["name"],
        email=data["email"],
        password=data["password"],
        role="TEACHER",
        school=data.get("school"),
        subject=data.get("subject") 
    )

    db.session.add(teacher)
    db.session.commit()

    return {"msg": "Teacher created"}
@bp.route("/stats")
@jwt_required()
def admin_stats():

    teachers = User.query.filter_by(role="TEACHER").count()

    students = Student.query.count()

    schools = db.session.query(User.school)\
    .filter(User.school != None)\
    .distinct()\
    .count()

    return {
        "teachers": teachers,
        "students": students,
        "schools": schools
    }
@bp.route("/schools", methods=["GET"])
@jwt_required()
def get_schools():

    uid = get_jwt_identity()
    admin = User.query.get(uid)

    if not admin or admin.role != "ADMIN":
        return {"error": "Unauthorized"}, 403

    schools = db.session.query(User.school)\
        .filter(User.school != None)\
        .distinct()\
        .all()

    return [s[0] for s in schools]

# ============================
# GET ALL TEACHERS
# ============================
@bp.route("/teachers", methods=["GET"])
@jwt_required()
def get_teachers():

    uid = get_jwt_identity()
    admin = User.query.get(uid)

    if not admin or admin.role != "ADMIN":
        return {"error": "Unauthorized"}, 403


    teachers = User.query.filter_by(role="TEACHER").all()

    data = []

    for t in teachers:

        data.append({

            "id": t.id,

            "name": t.name,

            "email": t.email,

            "school": t.school,

            "subject": t.subject

        })

    return data
# ============================
# DELETE TEACHER
# ============================
@bp.route("/delete-teacher/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_teacher(id):

    uid = get_jwt_identity()
    admin = User.query.get(uid)

    if not admin or admin.role != "ADMIN":
        return {"error":"Unauthorized"},403


    teacher = User.query.get(id)

    if not teacher or teacher.role != "TEACHER":
        return {"error":"Not found"},404


    db.session.delete(teacher)
    db.session.commit()

    return {"msg":"Deleted"}
# ===========================
# GET SUBJECTS
# ===========================
@bp.route("/subjects", methods=["GET"])
@jwt_required()
def get_subjects():

    uid = get_jwt_identity()
    admin = User.query.get(uid)

    if not admin or admin.role != "ADMIN":
        return {"error": "Unauthorized"}, 403

    subjects = db.session.query(User.subject)\
        .filter(User.subject != None)\
        .distinct()\
        .all()

    return [s[0] for s in subjects]
@bp.route("/analytics")
@jwt_required()
def admin_analytics():

    total_students = Student.query.count()
    total_teachers = User.query.filter_by(role="TEACHER").count()
    total_attendance = Attendance.query.count()

    active_students = db.session.query(
        Attendance.student_id
    ).distinct().count()

    health = 100

    if total_students > 0:
        health = round((active_students / total_students) * 100)

    return {
        "students": total_students,
        "teachers": total_teachers,
        "attendance": total_attendance,
        "active": active_students,
        "health": health
    }

from app.models.complaint import Complaint

@bp.route("/complaints")
@jwt_required()
def all_complaints():

    uid = get_jwt_identity()
    admin = User.query.get(uid)

    if admin.role != "ADMIN":
        return {"error": "Unauthorized"}, 403

    # ✅ ONLY NOT RESOLVED
    rows = Complaint.query.filter(
        Complaint.resolved_at == None
    ).order_by(
        Complaint.created_at.desc()
    ).all()

    data = []

    for c in rows:
        stu = Student.query.get(c.student_id)

        if not stu:
            continue

        data.append({
            "id": c.id,
            "student": stu.school,
            "roll": stu.roll_no,
            "msg": c.message,
            "status": c.status,
            "date": c.created_at.strftime("%d %b")
        })

    return data
    
@bp.route("/complaint/<int:id>/read", methods=["PUT"])
@jwt_required()
def read_complaint(id):

    uid = get_jwt_identity()
    admin = User.query.get(uid)

    if admin.role!="ADMIN":
        return {"error":"Unauthorized"},403


    c = Complaint.query.get(id)

    if not c:
        return {"error":"Not found"},404


    c.status="READ"
    c.read_at=datetime.utcnow()

    db.session.commit()

    return {"msg":"Marked read"}

from flask import request



@bp.route("/change-teacher-password", methods=["POST"])
@jwt_required()
def change_teacher_password():

    # ✅ Get logged-in user
    uid = get_jwt_identity()
    admin = User.query.get(uid)

    # ✅ Only ADMIN allowed
    if not admin or admin.role != "ADMIN":
        return {"error": "Unauthorized"}, 403

    # ✅ Get request data
    data = request.get_json()

    if not data:
        return {"error": "Invalid JSON"}, 400

    email = data.get("email")
    new_password = data.get("new_password")

    # ✅ Validation
    if not email or not new_password:
        return {"error": "Email and new password are required"}, 400

    # ✅ Find teacher in same school (important)
    teacher = User.query.filter_by(
        email=email,
        
    ).first()

    if not teacher:
        return {"error": "Teacher not found"}, 404

    # ✅ Update password (NO HASH as per your requirement)
    teacher.password = new_password

    db.session.commit()

    return {
        "message": f"Password updated successfully for {teacher.email}"
    }