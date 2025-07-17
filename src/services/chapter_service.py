import requests
from src.config import JSON_URL

def fetch_chapters():
    resp = requests.get(JSON_URL)
    resp.raise_for_status()
    return resp.json()

def get_json():
    resp = requests.get(JSON_URL)
    resp.raise_for_status()
    return resp.json()