import os
from src.config import STATE_FILE

def load_last_seen_chapter():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return f.read().strip()
    return None

def save_last_seen_chapter(chapter_id):
    with open(STATE_FILE, 'w') as f:
        f.write(chapter_id)