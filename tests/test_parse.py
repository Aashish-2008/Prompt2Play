import json
import re
import pytest

from backend import ollama_client


def test_extract_first_json_simple():
    txt = "Some text before {\"a\": 1, \"b\": [2,3]} some after"
    js = ollama_client.extract_first_json(txt)
    assert js is not None
    data = json.loads(js)
    assert data['a'] == 1
    assert data['b'] == [2,3]


def test_basic_rule_parse_hole():
    spec = ollama_client.basic_rule_parse('A growing hole that swallows objects')
    assert isinstance(spec, dict)
    assert spec.get('game_type') == 'Hole'
    assert 'swallow' in ' '.join(spec.get('mechanics', []))


def test_analyze_prompt_fallback(monkeypatch):
    # Force HTTP and CLI to fail so analyze_prompt uses rule-based fallback
    def fake_requests_post(*args, **kwargs):
        raise Exception('no http')
    monkeypatch.setattr('backend.ollama_client.requests.post', fake_requests_post)
    def fake_subprocess_run(*args, **kwargs):
        raise FileNotFoundError()
    monkeypatch.setattr('backend.ollama_client.subprocess.run', fake_subprocess_run)
    spec = ollama_client.analyze_prompt('A simple hole prompt for tests')
    assert isinstance(spec, dict)
    # fallback should return a Hole spec for this prompt
    assert spec.get('game_type') in ('Hole', 'Arcade')
