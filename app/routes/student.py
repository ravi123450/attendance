from datetime import datetime
from app.models.user import User
from flask import Blueprint, request, Response
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from app.models.student import Student
from app.models.attendance import Attendance
from app.models.notice import Notice
from app.extensions import db

import os
import csv
from io import StringIO


bp = Blueprint("student", __name__, url_prefix="/student")



# =========================
# LOGIN
# =========================
@bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    roll = data.get("roll_no")
    password = data.get("password")
    school = data.get("school")
    section = data.get("section")
    class_name = data.get("class_name")

    if not all([roll, password, school, section, class_name]):
        return {"error": "Missing fields"}, 400


    stu = Student.query.filter_by(
        roll_no=roll,
        school=school,
        section=section,
        class_name=class_name
    ).first()


    if not stu:
        return {"error": "Student not found"}, 401


    if not stu.check_password(password):
        return {"error": "Wrong password"}, 401


    token = create_access_token(identity=str(stu.id))

    return {
        "token": token,
        "id": stu.id
    }




# =========================
# DASHBOARD
# =========================
@bp.route("/dashboard")
@jwt_required()
def dashboard():

    sid = get_jwt_identity()

    stu = Student.query.get(sid)

    if not stu:
        return {"error": "User not found"}, 404


    records = Attendance.query.filter_by(
        student_id=sid
    ).order_by(Attendance.day.desc()).all()


    history = []
    print(records)
    for r in records:
        history.append({
            "date": r.day.strftime("%Y-%m-%d"),
            "time": r.time.strftime("%H:%M"),
            "method": r.method,
            "status": "Present" if r.method else "Absent"
        })
    print(history)

    # Latest notice
    notice = Notice.query.filter_by(
        school=stu.school
    ).order_by(Notice.created.desc()).first()


    return {
        "name": stu.name,
        "roll": stu.roll_no,
        "class": stu.class_name,
        "section": stu.section,
        "email": stu.email,
        "photo": stu.profile_pic,

        "total": len(records),

        "history": history,

        "notice": notice.message if notice else None
    }



# =========================
# UPDATE PROFILE
# =========================
@bp.route("/update", methods=["POST"])
@jwt_required()
def update_profile():

    uid = get_jwt_identity()

    stu = Student.query.get(uid)

    if not stu:
        return {"error": "User not found"}, 404


    email = request.form.get("email")
    password = request.form.get("password")
    photo = request.files.get("photo")


    UPLOAD_DIR = "uploads/students"
    os.makedirs(UPLOAD_DIR, exist_ok=True)


    if email:
        stu.email = email

    if password:
        stu.set_password(password)

    if photo:

        path = f"{UPLOAD_DIR}/{uid}.jpg"

        photo.save(path)

        stu.profile_pic = path


    db.session.commit()

    return {"msg": "Profile updated"}



# =========================
# DOWNLOAD CSV
# =========================
@bp.route("/attendance/csv")
@jwt_required()
def download_csv():

    sid = get_jwt_identity()

    rows = Attendance.query.filter_by(
        student_id=sid
    ).all()


    out = StringIO()
    writer = csv.writer(out)

    writer.writerow(["Date", "Time", "Method"])


    for r in rows:
        writer.writerow([
            r.day,
            r.time.strftime("%H:%M"),
            r.method
        ])


    return Response(
        out.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=attendance.csv"
        }
    )



# =========================
# GET NOTICES
# =========================
@bp.route("/notices")
@jwt_required()
def get_notices():

    sid = get_jwt_identity()

    stu = Student.query.get(sid)

    if not stu:
        return {"error": "User not found"}, 404


    rows = Notice.query.filter_by(
        school=stu.school   # ✅ Only same school
    ).order_by(
        Notice.created.desc()
    ).limit(5).all()


    return [
        {
            "title": "Alert",
            "msg": n.message,
            "date": n.created.strftime("%d %b")
        }
        for n in rows
    ]


@bp.route("/schools", methods=["GET"])
def get_public_schools():

    schools = db.session.query(User.school)\
        .filter(User.school != None)\
        .distinct()\
        .all()

    return [s[0] for s in schools]

@bp.route("/classes/<school>")
def get_classes(school):

    rows = db.session.query(Student.class_name)\
        .filter_by(school=school)\
        .distinct().all()

    return [r[0] for r in rows]

@bp.route("/sections/<school>/<class_name>")
def get_sections(school, class_name):

    rows = db.session.query(Student.section)\
        .filter_by(
            school=school,
            class_name=class_name
        ).distinct().all()

    return [r[0] for r in rows]

from app.models.activity import Activity
from app.models.activity_submission import ActivitySubmission

@bp.route("/activities")
@jwt_required()
def student_activities():

    sid = get_jwt_identity()
    stu = Student.query.get(sid)

    rows = Activity.query.filter_by(
        school=stu.school,
        class_name=stu.class_name,
        section=stu.section
    ).all()

    return [{
        "id": a.id,
        "title": a.title,
        "description": a.description,
        "date": a.created_at.strftime("%d %b")
    } for a in rows]

@bp.route("/activity/<int:id>", methods=["POST"])
@bp.route("/activity/<int:id>/submit", methods=["POST"])
@jwt_required()
def submit_activity(id):

    sid = get_jwt_identity()

    # ❗ Prevent multiple submissions
    exist = ActivitySubmission.query.filter_by(
        activity_id=id,
        student_id=sid
    ).first()

    exist = ActivitySubmission.query.filter_by(
        activity_id=id,
        student_id=sid
    ).first()

    if exist and exist.status != "REJECTED":
        return {"error":"Already submitted"},409


    file = request.files.get("photo")
    if exist and exist.status == "REJECTED":

        exist.photo = path
        exist.status = "PENDING"
        exist.submitted_at = datetime.utcnow()

        db.session.commit()

        return {"msg":"Resubmitted"}

    if not file:
        return {"error":"Photo required"},400


    path = f"uploads/activities/{sid}_{id}.jpg"
    file.save(path)


    sub = ActivitySubmission(
        activity_id=id,
        student_id=sid,
        photo=path,
        status="PENDING"   # default
    )

    db.session.add(sub)
    db.session.commit()

    return {"msg":"Submitted"}



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
            "activity_id": r.activity_id, 
            "title":act.title,
            "status":r.status,
            "date":r.submitted_at.strftime("%d %b")
        })

    return data

from app.models.complaint import Complaint


@bp.route("/complaint", methods=["POST"])
@jwt_required()
def raise_complaint():

    sid = get_jwt_identity()

    data = request.json
    msg = data.get("message")

    if not msg:
        return {"error":"Message required"},400


    # prevent spam (same text)
    last = Complaint.query.filter_by(
        student_id=sid,
        message=msg,
        status="OPEN"
    ).first()

    if last:
        return {"error":"Already submitted"},409


    c = Complaint(
        student_id=sid,
        message=msg
    )

    db.session.add(c)
    db.session.commit()

    return {"msg":"Complaint sent"}

@bp.route("/complaints")
@jwt_required()
def my_complaints():

    sid = get_jwt_identity()

    rows = Complaint.query.filter_by(
        student_id=sid
    ).order_by(Complaint.created_at.desc()).all()


    return [{
        "id":c.id,
        "msg":c.message,
        "status":c.status,
        "date":c.created_at.strftime("%d %b"),
        "read": bool(c.read_at)
    } for c in rows]

@bp.route("/complaint/<int:id>/resolve", methods=["PUT"])
@jwt_required()
def resolve_complaint(id):

    sid = get_jwt_identity()

    c = Complaint.query.get(id)

    if not c or c.student_id!=int(sid):
        return {"error":"Not found"},404


    c.status="RESOLVED"
    c.resolved_at=datetime.utcnow()

    db.session.commit()

    return {"msg":"Resolved"}
