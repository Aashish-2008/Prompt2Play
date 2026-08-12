import json
import re
from typing import Any

import requests

from app.services.llm import OllamaClient
from app.services.validation import validate_game_spec


def _safe_title(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return "Untitled Game"
    title = normalized.split()[:6]
    return " ".join(title).title()


def parse_game_prompt(prompt_text: str) -> dict:
    clean_prompt = (prompt_text or "").strip()
    if not clean_prompt:
        raise ValueError("Prompt text is required.")

    client = OllamaClient()
    if client.is_available():
        try:
            spec = client.describe_game(clean_prompt)
            validated = validate_game_spec(spec)
            if validated["valid"]:
                return validated["spec"]
        except (ValueError, TypeError, KeyError, RuntimeError, json.JSONDecodeError, requests.RequestException):
            pass

    lowered = clean_prompt.lower()
    platformer_tokens = ["platformer", "jump", "platform", "dash", "run", "side scroller", "ninja", "gate"]
    survival_tokens = ["survival", "zombie", "survive", "waves", "health", "rounds"]
    is_platformer = any(token in lowered for token in platformer_tokens)
    is_survival = any(token in lowered for token in survival_tokens)

    if is_platformer:
        genre = "platformer"
        game_type = "side_scroller"
        enemies = "robots" if "robot" in lowered else "enemy drones"
        items = "stars" if "star" in lowered else "power-ups"
        objective = "Navigate the level, defeat robotic enemies, and collect unlockable power-ups."
        win_condition = "Reach the end of the level and defeat the final robot guardian."
        lose_condition = "Take too much damage or fall off the stage."
    else:
        genre = "survival"
        game_type = "top_down"
        enemies = "zombies" if "zombie" in lowered else "hostile creatures"
        items = "medical kits" if "medical" in lowered or "kit" in lowered else "power-ups"
        objective = "Survive the onslaught while collecting resources and keeping the player alive."
        win_condition = "Defeat the final wave and keep the health bar above zero until the timer ends."
        lose_condition = "The player health reaches zero or the timer expires before the objective is met."

    spec = {
        "title": _safe_title(clean_prompt),
        "genre": genre,
        "game_type": game_type,
        "objective": objective,
        "win_condition": win_condition,
        "lose_condition": lose_condition,
        "enemies": enemies,
        "items": items,
    }

    return validate_game_spec(spec)["spec"]
