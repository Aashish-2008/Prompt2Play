import os
import zipfile
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, send_file, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import ProjectForm
from app.models import GameProject
from app.services.generator import create_project_zip, generate_game_project
from app.services.parser import parse_game_prompt
from app.services.validation import validate_game_spec

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def new_project():
    form = ProjectForm()
    if form.validate_on_submit():
        prompt_text = form.prompt_text.data.strip()
        parsed = parse_game_prompt(prompt_text)
        validation = validate_game_spec(parsed)
        if not validation["valid"]:
            for error in validation["errors"]:
                flash(error, "error")
            return render_template("projects/new.html", form=form)

        project = GameProject(
            title=form.title.data.strip() or parsed["title"],
            short_description=(parsed["objective"] or "Prompt to playable game"),
            prompt_text=prompt_text,
            genre=parsed["genre"],
            game_type=parsed["game_type"],
            objective=parsed["objective"],
            win_condition=parsed["win_condition"],
            lose_condition=parsed["lose_condition"],
            enemies=parsed["enemies"],
            items=parsed["items"],
            status="generated",
            user_id=current_user.id,
        )
        db.session.add(project)
        db.session.commit()

        project_dir = generate_game_project(project)
        project.status = "ready"
        project.project_dir = str(project_dir)

        export_folder = Path(project_dir).parent
        zip_path = create_project_zip(project_dir, export_folder)
        project.zip_path = str(zip_path)
        db.session.commit()

        flash("Game project generated successfully.", "success")
        return redirect(url_for("projects.detail", project_id=project.id))

    return render_template("projects/new.html", form=form)


@projects_bp.route("/projects/<int:project_id>")
@login_required
def detail(project_id):
    project = GameProject.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    return render_template("projects/detail.html", project=project)


@projects_bp.route("/projects/<int:project_id>/download")
@login_required
def download_project(project_id):
    project = GameProject.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    zip_path = project.zip_path
    if not zip_path or not os.path.exists(zip_path):
        flash("ZIP export is not available yet.", "error")
        return redirect(url_for("projects.detail", project_id=project.id))

    return send_file(zip_path, as_attachment=True, download_name=os.path.basename(zip_path))
