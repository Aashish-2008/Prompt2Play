# Prompt2Play

Prompt2Play is a Flask web app that converts a natural-language prompt into a structured game specification and emits a Godot 4 project skeleton ready for ZIP export.

## Features
- User registration and login
- Dashboard for game projects
- Rule-based game prompt parsing with Ollama fallback support
- Game specification validation
- Generated Godot project files and ZIP export
- SQLite-ready persistence with PostgreSQL migration path

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Then open http://127.0.0.1:5000

## Testing

```bash
pytest -q
```
