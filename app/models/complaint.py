from app.extensions import db
from datetime import datetime


class Complaint(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id"),
        nullable=False
    )

    message = db.Column(db.Text, nullable=False)

    status = db.Column(
        db.String(20),
        default="OPEN"  # OPEN / READ / RESOLVED
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    read_at = db.Column(db.DateTime)

    resolved_at = db.Column(db.DateTime)
