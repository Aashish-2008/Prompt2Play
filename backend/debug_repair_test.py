import json
import traceback
import ollama_client

repaired = '{"title":"Repaired","genre":"Puzzle","player_color":"#112233","enemy_color":"#334455","theme":"X","instructions":"Do"}'
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

def fake_post(url, payload=None, stream=None, timeout=None):
    return R(['data: ' + repaired])

orig = ollama_client.requests.post
ollama_client.requests.post = fake_post
try:
    out = ollama_client._repair_llm_json('{bad}', 'prompt', 'model')
    print('REPAIR OUT:', out)
except Exception as e:
    print('EXC:')
    traceback.print_exc()
finally:
    ollama_client.requests.post = orig
