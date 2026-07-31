import json

repaired = '{"title":"Repaired","genre":"Puzzle","player_color":"#112233","enemy_color":"#334455","theme":"X","instructions":"Do"}'
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

resp = R([stream_line])
assembled = ''
for raw in resp.iter_lines(decode_unicode=True):
    print('RAW LINE:', repr(raw))
    if not raw:
        continue
    raw = raw.strip()
    try:
        part = json.loads(raw)
        print('PARSED AS JSON:', part)
        if isinstance(part, dict) and 'response' in part:
            assembled += part.get('response') or ''
        elif isinstance(part, dict) and 'output' in part:
            assembled += part.get('output') or ''
    except Exception as e:
        print('JSON LOAD FAILED:', e)
        assembled += raw

print('ASSEMBLED:', repr(assembled))
candidate = None
# emulate extract_first_json
s = assembled
start = None
depth = 0
for i,ch in enumerate(s):
    if ch == '{':
        if start is None:
            start = i
        depth += 1
    elif ch == '}':
        if start is not None:
            depth -= 1
            if depth == 0:
                candidate = s[start:i+1]
                break
print('CANDIDATE:', candidate)
if candidate:
    try:
        parsed = json.loads(candidate)
        print('PARSED CANDIDATE:', parsed)
    except Exception as e:
        print('PARSE CANDIDATE FAILED:', e)
