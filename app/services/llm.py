import json
from urllib.error import HTTPError, URLError

import requests


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.ok
        except (requests.RequestException, HTTPError, URLError):
            return False

    def generate(self, prompt: str, model: str = "llama3.2") -> str:
        if not self.is_available():
            raise RuntimeError("Ollama is not running or unreachable.")

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1},
        }
        response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=12)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")

    def describe_game(self, text: str) -> dict:
        prompt = (
            "You are a game-design assistant. Return JSON only with keys: title, genre, "
            "game_type, objective, win_condition, lose_condition, enemies, items. "
            f"Prompt: {text}"
        )
        response_text = self.generate(prompt)
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("` ").replace("json\n", "").replace("\n", "")
        return json.loads(cleaned)
