import os
import json
from datetime import datetime

DATA_DIR = "data/history"

def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def get_user_file(username):
    ensure_dir()
    return os.path.join(DATA_DIR, f"{username}.json")

def verify_user(username, password):
    return (
        username == os.getenv("JARVIS_USER", "admin") and
        password == os.getenv("JARVIS_PASS", "1234")
    )

def load_history(username):
    path = get_user_file(username)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_record(username, record):
    data = load_history(username)
    data.insert(0, record)

    path = get_user_file(username)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def make_record(filename, language, ai_score, rule_score, final_score):
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": filename,
        "language": language,
        "ai_score": ai_score,
        "rule_score": rule_score,
        "final_score": final_score
    }