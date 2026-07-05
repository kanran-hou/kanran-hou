import json, re
def extract_json(text: str) -> dict:
    m = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if m:
        try: return json.loads(m.group())
        except: pass
    return {}
