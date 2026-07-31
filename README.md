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

References and inspiration
- Hole-mechanic ideas and design notes: https://in.pinterest.com/nohaelgendi/2d-games/
- Community game ideas and mechanics: https://www.reddit.com/r/gamedesign/comments/13d9sso/2d_game_ideas/
- Question-based brainstorming (Quora): https://www.quora.com/What-are-some-good-ideas-for-developing-2D-games
- Unity 2D perspective reference (useful for physics and camera): https://docs.unity3d.com/6000.0/Documentation/Manual/2d-game-perspective-reference.html

Hole Game (The Growing Abyss)
This repository now includes a simple hole-mechanic prototype generator. When a prompt or parsed spec mentions "hole", "black hole" or specifies game_type: "hole", the generator outputs a top-down growing-hole prototype. The prototype demonstrates:
- Real-time growth by absorbing objects
- Simple collision / trigger logic using radii
- Visual soft-edge hole rendering and object spawning

Storyline & credit
- Storyline (example): "The city is sinking into the Growing Abyss. You control a small void that feeds on everyday objects. Grow quickly to swallow larger structures before time runs out, and discover why the abyss awakens."
- Credits: design inspired by community posts and Hole.io-like mechanics. See references above.

How to try the hole prototype
1. Start the server (python backend/app.py).
2. In the web UI, include 'hole' or 'black hole' in your prompt, or edit the returned spec and set game_type to 'hole'.
3. Preview and play; generated HTML files are saved to backend/generated_games/ and can be downloaded or opened directly.

Enhancements added
- Backend game generator now recognizes hole-mechanic prompts and emits a playable hole prototype (HTML5 canvas).
- README updated with references, storyline, and usage notes.

