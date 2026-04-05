from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.extensions import db

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    user = User.query.filter_by(email=data["email"]).first()

    if not user:
        return {"error": "User not found"}, 401

    if user.password != data["password"]:
        return {"error": "Wrong password"}, 401

    token = create_access_token(identity=str(user.id))

    return {
        "token": token,
        "role": user.role,
        "user_id": user.id
    }
