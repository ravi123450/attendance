from app.extensions import db
from datetime import datetime


class ActivitySubmission(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    activity_id = db.Column(
        db.Integer,
        db.ForeignKey("activity.id")
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id")
    )

    photo = db.Column(db.String(255))

    status = db.Column(
        db.String(20),
        default="PENDING"
    )  # PENDING / APPROVED / REJECTED

    submitted_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
