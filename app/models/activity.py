from app.extensions import db
from datetime import datetime

class Activity(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)

    school = db.Column(db.String(100))
    class_name = db.Column(db.String(50))
    section = db.Column(db.String(20))

    created_by = db.Column(db.Integer)   # teacher id

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
