import asyncio
from src.config import CHAT_ID, IMAGE_FOLDER, PDF_FOLDER
from src.services.chapter_service import get_json
from src.utils.pdf_utils import download_images, generate_pdf
from src.utils.file_utils import load_last_seen_chapter, save_last_seen_chapter
from telegram import InputFile
import logging
import os

logger = logging.getLogger(__name__)

async def poll_for_new_chapters(application):
    while True:
        try:
            data = get_json()
            chapters = data.get("chapters", {})
            latest_id, latest = max(
                chapters.items(),
                key=lambda item: item[1].get("last_updated", 0)
            )
            title = latest.get("title", "Untitled")
            images = latest.get("groups", {}).get("/r/OnePunchMan", [])
            last_seen = load_last_seen_chapter()

            if latest_id != last_seen:
                logger.info(f"New chapter: {title}")
                image_paths = download_images(images, IMAGE_FOLDER)
                filename = f"{title.replace(' ', '_')}.pdf"
                pdf_path = os.path.join(PDF_FOLDER, filename)
                generate_pdf(image_paths, pdf_path)

                with open(pdf_path, 'rb') as f:
                    await application.bot.send_document(
                        chat_id=CHAT_ID,
                        document=InputFile(f, filename=filename),
                        caption=f"New chapter released: {title}"
                    )
                save_last_seen_chapter(latest_id)
            else:
                logger.info("No new chapter found.")
        except Exception as e:
            logger.exception(f"Error in polling: {type(e).__name__}: {e}")
        await asyncio.sleep(1800)

async def on_startup(application):
    application.create_task(poll_for_new_chapters(application))
    logger.info("Started background task for chapter polling.")

