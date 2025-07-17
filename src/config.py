import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
JSON_URL = os.getenv("JSON_URL")
STATE_FILE = "last_seen_chapter.txt"
PDF_FOLDER = "opm_chapters"
IMAGE_FOLDER = "images"
CHAPTERS_PER_PAGE = 10
