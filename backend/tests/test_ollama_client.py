import json
import types
import pytest

from ollama_client import extract_first_json, basic_rule_parse, analyze_prompt, _repair_llm_json

class MockResp:
    def __init__(self, lines=None, text=''):
        self._lines = lines or []
        self.text = text or '\n'.join(self._lines)
    def iter_lines(self, decode_unicode=True):
        for l in self._lines:
            yield l
    def json(self):
        try:
            return json.loads(self.text)
        except Exception:
            raise


def test_extract_first_json_simple():
    s = 'Some intro {"a":1, "b":{"c":2}} trailing'
    out = extract_first_json(s)
    assert out is not None
    assert out.startswith('{') and out.endswith('}')
    parsed = json.loads(out)
    assert parsed['a'] == 1 and parsed['b']['c'] == 2


def test_basic_rule_parse_zombie():
    spec = basic_rule_parse('Big zombie survival arena')
    assert isinstance(spec, dict)
    assert 'Zombie' in spec.get('title') or spec.get('genre') == 'Shooter' or 'zombie' in spec.get('theme','').lower()


def test_analyze_prompt_fallback_rule(monkeypatch):
    # Simulate requests.post raising and subprocess.run raising so analyze_prompt falls back
    import requests, subprocess
    def fake_post(*args, **kwargs):
        raise Exception('no http')
    def fake_run(*args, **kwargs):
        raise FileNotFoundError()
    monkeypatch.setattr('ollama_client.requests.post', fake_post)
    monkeypatch.setattr('ollama_client.subprocess.run', fake_run)
    spec = analyze_prompt('completely arbitrary prompt that triggers fallback', strict=False)
    assert isinstance(spec, dict)
    assert 'prompt' in spec and spec['prompt'].startswith('completely arbitrary')
    assert 'title' in spec


def test_repair_llm_json_from_stream(monkeypatch):
    # Simulate a repair response that streams a JSON object as a single line
    repaired = '{"title":"Repaired","genre":"Puzzle","player_color":"#112233","enemy_color":"#334455","theme":"X","instructions":"Do stuff"}'
    def fake_post(url, json=None, stream=None, timeout=None):
        return MockResp(lines=[repaired], text=repaired)
    monkeypatch.setattr('ollama_client.requests.post', fake_post)
    out = _repair_llm_json('{bad json}', 'user prompt', 'dummy-model')
    assert isinstance(out, dict)
    assert out.get('title') == 'Repaired'

# Basic smoke to ensure module imports and functions exist
def test_sanity_imports():
    assert extract_first_json is not None
    assert basic_rule_parse is not None
    assert analyze_prompt is not None
