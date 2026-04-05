# from flask import Blueprint, request
# from flask_jwt_extended import create_access_token
# from app.models.student import Student

# bp = Blueprint("student_auth", __name__, url_prefix="/student2")


# @bp.route("/login", methods=["POST"])
# def student_login():

#     data = request.json

#     roll = data.get("roll_no")
#     password = data.get("password")

#     # Find student
#     student = Student.query.filter_by(roll_no=roll).first()

#     if not student:
#         return {"error": "Invalid credentials"}, 401


#     # ✅ IMPORTANT: Check hashed password
#     if not student.check_password(password):
#         return {"error": "Invalid credentials"}, 401


#     # Generate token
#     token = create_access_token(identity=f"student:{student.id}")
#     return {
#         "token": token,
#         "id": student.id,
#         "name": student.name,
#         "roll": student.roll_no,
#         "role": "STUDENT"
#     }
