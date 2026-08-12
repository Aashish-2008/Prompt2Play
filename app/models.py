from datetime import datetime, timezone

from flask_login import UserMixin

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    projects = db.relationship("GameProject", backref="owner", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


class GameProject(db.Model):
    __tablename__ = "game_projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    short_description = db.Column(db.Text, nullable=False)
    prompt_text = db.Column(db.Text, nullable=False)
    genre = db.Column(db.String(50), nullable=False, default="survival")
    game_type = db.Column(db.String(50), nullable=False, default="top_down")
    objective = db.Column(db.Text, nullable=False)
    win_condition = db.Column(db.Text, nullable=False)
    lose_condition = db.Column(db.Text, nullable=False)
    enemies = db.Column(db.String(120), nullable=False, default="hostiles")
    items = db.Column(db.String(120), nullable=False, default="power-ups")
    status = db.Column(db.String(30), nullable=False, default="draft")
    project_dir = db.Column(db.String(255), nullable=True)
    zip_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<GameProject {self.title}>"
