from pathlib import Path
import json
def log_request(trace_id, query, intent, duration):
    path=Path("logs.jsonl")
    entry={
        "trace_id":trace_id,
        "query":query,
        "intent":intent,
        "duration":duration
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry)+"\n")