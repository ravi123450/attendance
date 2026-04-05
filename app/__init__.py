from flask import Flask
from .extensions import db, migrate, jwt
from flask_cors import CORS
from app.models.user import User



def create_app():
    app = Flask(__name__)
    import os

    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


    # Serve uploads folder
    @app.route("/uploads/<path:filename>")
    def uploaded_files(filename):
        from flask import send_from_directory
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    app.config.from_object("app.config.Config")

    CORS(app, supports_credentials=True)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    with app.app_context():

        db.create_all()

        # Create default admin
        admin = User.query.filter_by(role="ADMIN").first()

        if not admin:

            default_admin = User(
                name="Admin",
                email="admin@school.com",
                password="admin123",
                role="ADMIN"
            )

            db.session.add(default_admin)
            db.session.commit()

            print("✅ Default Admin Created")


    from .routes import auth, admin, teacher, student, attendance
    from app.routes.student import bp as student_bp
    from app.routes.attendance_alerts import alerts_bp


    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(teacher.bp)
    app.register_blueprint(attendance.bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(alerts_bp)

    
    

    return app
    