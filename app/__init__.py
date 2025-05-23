from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate  # ✅ جديد
from app.models import db, User
from app.routes import main
from app.auth_routes import auth
from app.api.routes import api  # ✅ API

login_manager = LoginManager()
migrate = Migrate()  # ✅ جديد

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # تهيئة قواعد البيانات و Login
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)  # ✅ جديد

    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # تسجيل جميع Blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(api)  # ✅ API

    return app
