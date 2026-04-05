from datetime import datetime
from app.extensions import db


class Notice(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))
    message = db.Column(db.Text)

    school = db.Column(db.String(100)) 

    created = db.Column(db.DateTime, default=datetime.utcnow)
