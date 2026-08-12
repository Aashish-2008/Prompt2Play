from flask import Flask, request, jsonify, send_from_directory, session
from pathlib import Path
import json
import time
import os
from game_generator import generate_game_html
from ollama_client import analyze_prompt
from db import init_db, create_user, authenticate_user, save_project, get_projects_by_user, get_user_by_id
from godot_exporter import create_godot_zip
from flask import send_file
import io

BASE_DIR = Path(__file__).resolve().parent
GENERATED_DIR = BASE_DIR.parent / 'generated_games'
GENERATED_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = BASE_DIR / 'db.sqlite'

# Initialize DB
init_db(str(DB_PATH))

app = Flask(__name__, static_folder=str(BASE_DIR.parent / 'frontend'))
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    username = data.get('username','').strip()
    email = data.get('email','').strip()
    password = data.get('password','')
    if not username or not password:
        return jsonify({'error':'username and password required'}), 400
    try:
        user_id = create_user(str(DB_PATH), username, email, password)
        session['user_id'] = user_id
        return jsonify({'status':'ok','user_id':user_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username','').strip()
    password = data.get('password','')
    if not username or not password:
        return jsonify({'error':'username and password required'}), 400
    user = authenticate_user(str(DB_PATH), username, password)
    if not user:
        return jsonify({'error':'invalid credentials'}), 401
    session['user_id'] = user['id']
    return jsonify({'status':'ok','user':{'id':user['id'],'username':user['username']}})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user_id', None)
    return jsonify({'status':'ok'})

@app.route('/api/me')
def api_me():
    uid = session.get('user_id')
    if not uid:
        return jsonify({'user': None})
    user = get_user_by_id(str(DB_PATH), uid)
    if not user:
        return jsonify({'user': None})
    return jsonify({'user':{'id': user['id'], 'username': user['username']}})

@app.route('/api/projects')
def api_projects():
    uid = session.get('user_id')
    if not uid:
        return jsonify({'projects': []})
    projects = get_projects_by_user(str(DB_PATH), uid)
    return jsonify({'projects': projects})

@app.route('/api/parse', methods=['POST'])
def api_parse():
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return jsonify({'error': 'prompt required'}), 400
    strict = bool(data.get('strict', False))
    spec = analyze_prompt(prompt, strict=strict)
    return jsonify({'spec': spec})


@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    if not prompt and not data.get('spec'):
        return jsonify({'error': 'prompt required'}), 400

    # If frontend provided an edited spec, use it directly (validation UI). Otherwise parse the prompt.
    spec = data.get('spec')
    if spec:
        # ensure prompt field exists for provenance
        prompt = spec.get('prompt', prompt)
    else:
        strict = bool(data.get('strict', False))
        spec = analyze_prompt(prompt, strict=strict)

    # Allow frontend to pass an explicit game_type (template selector)
    game_type = data.get('game_type')
    if game_type:
        try:
            spec['game_type'] = game_type
            # if genre not set, use game_type as genre to influence generator
            if not spec.get('genre'):
                spec['genre'] = game_type
        except Exception:
            pass

    # Generate a playable HTML5 game using the spec
    html = generate_game_html(spec)
    ts = int(time.time())
    filename = f'game_{ts}.html'
    outpath = GENERATED_DIR / filename
    outpath.write_text(html, encoding='utf-8')

    # Save project if user logged in
    uid = session.get('user_id')
    try:
        if uid:
            save_project(str(DB_PATH), uid, prompt, spec.get('title') or spec.get('genre') or 'Untitled', spec.get('genre'), filename)
    except Exception as e:
        # log but continue
        print('Failed to save project:', e)

    preview_url = f'/preview/{filename}'
    return jsonify({'preview': preview_url, 'spec': spec})

@app.route('/preview/<path:filename>')
def preview(filename):
    path = GENERATED_DIR / filename
    if not path.exists():
        return 'Not found', 404
    return send_from_directory(str(GENERATED_DIR), filename)

@app.route('/api/export_godot', methods=['POST'])
def api_export_godot():
    data = request.get_json() or {}
    spec = data.get('spec')
    prompt = data.get('prompt','')
    if not spec:
        if not prompt:
            return jsonify({'error':'spec or prompt required'}), 400
        spec = analyze_prompt(prompt, strict=bool(data.get('strict', False)))

    try:
        zbytes = create_godot_zip(spec)
        bio = io.BytesIO(zbytes)
        bio.seek(0)
        return send_file(bio, mimetype='application/zip', as_attachment=True, download_name='prompt2play_godot.zip')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    return jsonify({'status':'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
