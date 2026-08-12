from flask import Flask

from app.config import Config
from app.extensions import db, login_manager
from app.models import GameProject, User
from app.routes import auth_bp, dashboard_bp, projects_bp


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    app.config.setdefault("SECRET_KEY", "dev-secret-key")
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///prompt2play.db")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp)

    with app.app_context():
        db.create_all()

    return app
