from __future__ import annotations


def validate_game_spec(spec: dict) -> dict:
    errors = []
    required = ["title", "genre", "game_type", "objective", "win_condition", "lose_condition", "enemies", "items"]

    for key in required:
        value = spec.get(key)
        if value is None or not str(value).strip():
            errors.append(f"Missing field: {key}")

    if spec.get("genre") not in {"survival", "platformer", "action", "racing"}:
        errors.append("Unsupported genre. Use survival, platformer, action, or racing.")

    normalized = dict(spec)
    normalized["title"] = str(normalized.get("title", "Untitled Game")).strip() or "Untitled Game"
    normalized["genre"] = str(normalized.get("genre", "survival")).strip().lower()
    normalized["game_type"] = str(normalized.get("game_type", "top_down")).strip().lower()
    normalized["objective"] = str(normalized.get("objective", "Complete the main challenge.")).strip()
    normalized["win_condition"] = str(normalized.get("win_condition", "Complete the objective without losing all health.")).strip()
    normalized["lose_condition"] = str(normalized.get("lose_condition", "Lose all health or the timer reaches zero.")).strip()
    normalized["enemies"] = str(normalized.get("enemies", "hostiles")).strip()
    normalized["items"] = str(normalized.get("items", "power-ups")).strip()

    return {"valid": not errors, "errors": errors, "spec": normalized}
