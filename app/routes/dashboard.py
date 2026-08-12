from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models import GameProject


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    projects = GameProject.query.filter_by(user_id=current_user.id).order_by(GameProject.created_at.desc()).all()
    return render_template("dashboard.html", projects=projects)
