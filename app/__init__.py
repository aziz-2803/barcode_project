from flask import Flask
from flask_login import LoginManager
from app.models import db, User
from app.routes import main
from app.auth_routes import auth  # إذا كنت تستخدم تسجيل دخول

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'  # اسم دالة تسجيل الدخول

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(main)
    app.register_blueprint(auth)  # لو عندك auth_routes.py

    return app
