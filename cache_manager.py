import json, time
from pathlib import Path

CACHE_FILE = Path("cache.json")

def load_cache():
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except Exception:
            return {}
    return {}

def save_cache(data):
    try:
        CACHE_FILE.write_text(json.dumps(data))
    except Exception:
        pass

def cache_get(key, max_age_seconds=300):
    data = load_cache()
    if key in data:
        entry = data[key]
        if time.time() - entry.get("ts", 0) < max_age_seconds:
            return entry.get("value")
    return None

def cache_set(key, value):
    data = load_cache()
    data[key] = {"ts": time.time(), "value": value}
    save_cache(data)
