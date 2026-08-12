import zipfile

from app import create_app
from app.services.generator import create_project_zip, generate_game_project


class DummyOwner:
    username = "tester"


class DummyProject:
    def __init__(self):
        self.id = 42
        self.title = "Ninja Run // 2"
        self.objective = "Escape the neon city and reach the final gate."
        self.win_condition = "Reach the final gate without losing all health."
        self.lose_condition = "The hero runs out of health."
        self.owner = DummyOwner()


def test_generate_game_project_and_zip():
    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, SQLALCHEMY_DATABASE_URI="sqlite://")

    with app.app_context():
        project = DummyProject()
        project_dir = generate_game_project(project)

        assert project_dir.exists()
        assert (project_dir / "project.godot").exists()
        assert (project_dir / "scenes" / "Main.tscn").exists()
        assert (project_dir / "scripts" / "Main.gd").exists()

        zip_path = create_project_zip(project_dir, project_dir.parent)
        assert zip_path.exists()

        with zipfile.ZipFile(zip_path, "r") as archive:
            names = set(archive.namelist())
            assert "project.godot" in names
            assert "README.md" in names
            assert "scenes/Main.tscn" in names
            assert "scripts/Main.gd" in names
