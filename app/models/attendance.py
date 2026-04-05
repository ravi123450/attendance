from app.extensions import db
from datetime import date, datetime


class Attendance(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id"),
        nullable=False
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    day = db.Column(db.Date, default=date.today)

    time = db.Column(db.DateTime, default=datetime.utcnow)

    status = db.Column(db.String(20), default="PRESENT")

    method = db.Column(db.String(10))  # FACE / QR
