import os

from PIL import Image
from io import BytesIO
import requests
import img2pdf
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Bot, InputFile

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("chapter_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load credentials
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

JSON_URL = "https://gist.githubusercontent.com/funkyhippo/1d40bd5dae11e03a6af20e5a9a030d81/raw"
STATE_FILE = "last_seen_chapter.txt"
PDF_FOLDER = "opm_chapters"
IMAGE_FOLDER = "images"

def get_json():
    resp = requests.get(JSON_URL)
    resp.raise_for_status()
    return resp.json()

def get_latest_chapter(data):
    chapters = data.get("chapters", {})
    if not chapters:
        return None

    latest_id, latest = max(
        chapters.items(),
        key=lambda item: item[1].get("last_updated", 0)
    )

    return {
        "id": latest_id,
        "title": latest.get("title", "Untitled Chapter"),
        "images": latest.get("groups", {}).get("/r/OnePunchMan", []),
        "volume": latest.get("volume", None),
        "last_updated": latest.get("last_updated", None)
    }

def load_last_seen_chapter():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return f.read().strip()
    return None

def save_last_seen_chapter(chapter_id):
    with open(STATE_FILE, 'w') as f:
        f.write(chapter_id)


def download_images(image_urls, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    paths = []
    for i, url in enumerate(image_urls):
        response = requests.get(url)
        response.raise_for_status()

        # Open image and compress it using Pillow
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img_path = os.path.join(output_folder, f"page_{i + 1}.jpg")

        # Save with light compression (quality ~85 is good balance)
        img.save(img_path, format='JPEG', quality=85, optimize=True)

        paths.append(img_path)
        logger.info(f"Downloaded and compressed image {i + 1}/{len(image_urls)}")
    return paths

def generate_pdf(image_paths, output_pdf):
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    with open(output_pdf, "wb") as f:
        f.write(img2pdf.convert(image_paths))
    logger.info(f"PDF generated: {output_pdf}")

    for img_file in image_paths:
        try:
            os.remove(img_file)
        except Exception as e:
            logger.warning(f"Failed to delete image {img_file}: {e}")

    logger.info(f"Images deleted.")

async def send_pdf_to_telegram(pdf_path, chapter_title):
    async with bot:
        with open(pdf_path, 'rb') as f:
            await bot.send_document(
                chat_id=CHAT_ID,
                document=InputFile(f, filename=os.path.basename(pdf_path)),
                caption=f"New chapter released: {chapter_title}"
            )
    logger.info(f"Sent PDF to Telegram: {pdf_path}")

async def main():
    while True:
        try:
            data = get_json()
            latest_chapter = get_latest_chapter(data)
            if not latest_chapter:
                logger.warning("No chapters found in JSON.")
                await asyncio.sleep(900)
                continue

            chapter_id = latest_chapter.get("id")
            chapter_title = latest_chapter.get("title", "Untitled Chapter")
            image_urls = latest_chapter.get("images", [])

            last_seen = load_last_seen_chapter()

            if chapter_id != last_seen:
                logger.info(f"New chapter detected: {chapter_title}")
                pdf_filename = f"{chapter_title.replace(' ', '_')}.pdf"
                pdf_path = os.path.join(PDF_FOLDER, pdf_filename)

                image_paths = download_images(image_urls, IMAGE_FOLDER)
                generate_pdf(image_paths, pdf_path)
                await send_pdf_to_telegram(pdf_path, chapter_title)
                save_last_seen_chapter(chapter_id)
            else:
                logger.info("No new chapter.")

        except Exception as e:
            logger.exception(f"An error occurred during execution: {type(e).__name__}: {e}")

        await asyncio.sleep(900)  # Check every 5 minutes

if __name__ == "__main__":
    asyncio.run(main())
