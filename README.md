# Prompt2Play — AI-Powered 2D Game Generator (Prototype)

This prototype scaffolds a local web app that converts a short prompt into a playable HTML5 game prototype.

Stack (defaults used):
- Backend: Flask
- Frontend: Static HTML + Tailwind (CDN)
- AI engine: Ollama (local) — wrapper included with fallbacks
- Game preview: Single-file HTML5 prototype generated per prompt

Getting started
1. Install Python dependencies (recommended in a venv):

   python -m venv .venv
   .venv\Scripts\activate
   pip install -r backend/requirements.txt

2. Install Ollama and download a model (see https://ollama.ai/docs). Set OLLAMA_MODEL environment variable if you want a specific model.

3. Run the app:

   python backend/app.py

4. Open http://localhost:5000 in your browser and enter a prompt.

Notes
- If Ollama is not reachable, the server uses a simple rule-based parser and still generates a playable prototype.
- Generated games are saved to backend/generated_games/*.html and can be downloaded.

Next steps (can be implemented):
- Integrate richer LLM prompts and structured JSON output
- Asset generation pipeline (sprites/audio)
- Godot project export
- User accounts, project history, downloads

