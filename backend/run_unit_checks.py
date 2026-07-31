import json
import sys
from ollama_client import extract_first_json, basic_rule_parse, _repair_llm_json, analyze_prompt

failures = []

# test extract
try:
    s = 'prefix {"a":1,"b":{"c":2}} suffix'
    out = extract_first_json(s)
    parsed = json.loads(out)
    assert parsed['a']==1 and parsed['b']['c']==2
    print('PASS: extract_first_json')
except Exception as e:
    print('FAIL: extract_first_json', e)
    failures.append('extract')

# test basic_rule_parse
try:
    spec = basic_rule_parse('zombie horde')
    assert isinstance(spec, dict) and ('Zombie' in (spec.get('title') or '') or spec.get('genre')=='Shooter')
    print('PASS: basic_rule_parse')
except Exception as e:
    print('FAIL: basic_rule_parse', e)
    failures.append('basic_rule_parse')

# test repair function using mocked requests.post by monkeypatching in runtime
try:
    # create fake response via inner function and monkeypatch requests.post
    import ollama_client, types
    def fake_post(url, payload=None, stream=None, timeout=None):
        repaired = '{"title":"Repaired","genre":"Puzzle","player_color":"#112233","enemy_color":"#334455","theme":"X","instructions":"Do"}'
        # yield as a non-JSON-prefixed line so streaming parser appends raw text and extraction finds the JSON
        stream_line = 'data: ' + repaired
        class R:
            def __init__(self, lines):
                self._lines = lines
                self.text = '\n'.join(lines)
            def iter_lines(self, decode_unicode=True):
                for l in self._lines:
                    yield l
            def json(self):
                try:
                    return json.loads(self.text)
                except Exception:
                    raise
        return R([stream_line])
    orig = ollama_client.requests.post
    ollama_client.requests.post = fake_post
    out = _repair_llm_json('{bad}', 'prompt', 'model')
    ollama_client.requests.post = orig
    assert isinstance(out, dict) and out.get('title')=='Repaired'
    print('PASS: _repair_llm_json')
except Exception as e:
    print('FAIL: _repair_llm_json', e)
    failures.append('repair')

# test analyze_prompt fallback (force failures)
try:
    import ollama_client
    def bad_post(*args, **kwargs):
        raise Exception('no http')
    def bad_run(*args, **kwargs):
        raise FileNotFoundError()
    orig_post = ollama_client.requests.post
    orig_run = ollama_client.subprocess.run
    ollama_client.requests.post = bad_post
    ollama_client.subprocess.run = bad_run
    spec = analyze_prompt('this will fallback', strict=False)
    ollama_client.requests.post = orig_post
    ollama_client.subprocess.run = orig_run
    assert isinstance(spec, dict) and 'prompt' in spec
    print('PASS: analyze_prompt fallback')
except Exception as e:
    print('FAIL: analyze_prompt fallback', e)
    failures.append('analyze')

if failures:
    print('\nSOME CHECKS FAILED:', failures)
    sys.exit(2)
else:
    print('\nALL CHECKS PASSED')
    sys.exit(0)
