# from flask import Blueprint, request, Response
# from flask_jwt_extended import jwt_required, get_jwt_identity

# from app.models.student import Student
# from app.models.attendance import Attendance
# from app.extensions import db

# import csv
# from io import StringIO

# bp = Blueprint("student", __name__, url_prefix="/student")


# # ======================
# # DASHBOARD
# # ======================
# @bp.route("/dashboard")
# @jwt_required()
# def dashboard():

#     sid = get_jwt_identity()

#     stu = Student.query.get(sid)

#     if not stu:
#         return {"error": "Student not found"}, 404


#     records = Attendance.query.filter_by(
#         student_id=sid
#     ).order_by(Attendance.day.desc()).all()


#     data = []

#     for r in records:
#         data.append({
#             "date": r.day.strftime("%Y-%m-%d"),
#             "time": r.time.strftime("%H:%M"),
#             "method": r.method
#         })


#     return {
#         "name": stu.name,
#         "roll": stu.roll_no,
#         "class": stu.class_name,
#         "section": stu.section,
#         "email": stu.email,
#         "photo": stu.profile_pic,

#         "total": len(records),
#         "present": len(records),

#         "history": data
#     }


# # ======================
# # GET PROFILE
# # ======================
# @bp.route("/me")
# @jwt_required()
# def me():

#     sid = get_jwt_identity()

#     stu = Student.query.get(sid)

#     if not stu:
#         return {"error": "Not found"}, 404


#     return {
#         "name": stu.name,
#         "roll": stu.roll_no,
#         "class": stu.class_name,
#         "section": stu.section,
#         "email": stu.email,
#         "photo": stu.profile_pic
#     }


# # ======================
# # UPDATE PROFILE
# # ======================
# @bp.route("/update", methods=["POST"])
# @jwt_required()
# def update():

#     sid = get_jwt_identity()

#     stu = Student.query.get(sid)

#     if not stu:
#         return {"error": "Not found"}, 404


#     email = request.form.get("email")
#     password = request.form.get("password")
#     photo = request.files.get("photo")


#     if email:
#         stu.email = email

#     if password:
#         stu.set_password(password)

#     if photo:
#         path = f"uploads/students/{sid}.jpg"
#         photo.save(path)
#         stu.profile_pic = path


#     db.session.commit()

#     return {"msg": "Updated"}


# # ======================
# # CSV REPORT
# # ======================
# @bp.route("/attendance/csv")
# @jwt_required()
# def csv_report():

#     sid = get_jwt_identity()

#     rows = Attendance.query.filter_by(
#         student_id=sid
#     ).all()


#     out = StringIO()
#     writer = csv.writer(out)

#     writer.writerow(["Date", "Time", "Method"])

#     for r in rows:
#         writer.writerow([
#             r.day,
#             r.time.strftime("%H:%M"),
#             r.method
#         ])


#     resp = Response(
#         out.getvalue(),
#         mimetype="text/csv"
#     )

#     resp.headers["Content-Disposition"] = "attachment; filename=attendance.csv"

#     return resp
