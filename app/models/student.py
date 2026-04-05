from app.extensions import db
from werkzeug.security import check_password_hash, generate_password_hash


class Student(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    roll_no = db.Column(db.String(50), nullable=False)

    class_name = db.Column(db.String(50))

    section = db.Column(db.String(20))

    __table_args__ = (
    db.UniqueConstraint('roll_no', 'school', 'section',name='uix_roll_school_section'),
)


    # Login fields
    email = db.Column(db.String(120), unique=True, nullable=True)

    profile_pic = db.Column(db.String(255), nullable=True) 

    password = db.Column(db.String(255), nullable=False)

    # Face
    face_embedding = db.Column(db.PickleType, nullable=True)

    # QR
    qr_code = db.Column(db.String(255), unique=True)
    qr_image = db.Column(db.String(255))

    attendances = db.relationship("Attendance", backref="student")

    school = db.Column(db.String(100))

    # =====================
    # Password helpers
    # =====================

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
