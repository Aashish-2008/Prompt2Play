from app.services.parser import parse_game_prompt


def test_parse_survival_prompt():
    spec = parse_game_prompt(
        "A top-down zombie survival game where the player collects medical kits, fights waves of zombies, and wins by surviving five rounds."
    )
    assert spec["genre"] == "survival"
    assert spec["game_type"] == "top_down"
    assert "zombie" in spec["enemies"].lower() or "hostile" in spec["enemies"].lower()
    assert "medical" in spec["items"].lower() or "power" in spec["items"].lower()


def test_parse_platformer_prompt():
    spec = parse_game_prompt(
        "A futuristic ninja platformer where the hero dashes through laser robots and collects glowing stars before reaching the final gate."
    )
    assert spec["genre"] == "platformer"
    assert spec["game_type"] == "side_scroller"
    assert "robot" in spec["enemies"].lower() or "drone" in spec["enemies"].lower()
