import json
from pathlib import Path
def load_fun(conversation_id):
    path=Path("memory.json")
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get(conversation_id, [])
    else:
        return []
def save_fun(conversation_id,history):
    path=Path("memory.json")
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        data[conversation_id]=history
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    else:
        data = {}
        data[conversation_id]=history
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
if __name__=="__main__":
    save_fun("123",[])