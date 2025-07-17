from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
from src.config import CHAPTERS_PER_PAGE, IMAGE_FOLDER, PDF_FOLDER
from html import escape
from datetime import datetime
import os
import logging

from src.services.chapter_service import get_json
from src.utils.pdf_utils import download_images, generate_pdf

logger = logging.getLogger(__name__)


async def get_chapter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("chapter_refs"):
        await update.message.reply_text("Please run /list first to load chapters.")
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /get <chapter number from list>")
        return

    idx = int(context.args[0]) - 1
    chapter_refs = context.user_data["chapter_refs"]
    if idx < 0 or idx >= len(chapter_refs):
        await update.message.reply_text("Invalid chapter number.")
        return

    chap_id, chap_data = chapter_refs[idx]
    title = chap_data.get("title", "Untitled")
    images = chap_data.get("groups", {}).get("/r/OnePunchMan", [])

    filename = f"{title.replace(' ', '_')}.pdf"
    pdf_path = os.path.join(PDF_FOLDER, filename)

    if os.path.exists(pdf_path):
        logger.info(f"Reusing cached PDF: {pdf_path}")
    else:
        logger.info(f"Downloading chapter: {title}")
        image_paths = download_images(images, IMAGE_FOLDER)
        generate_pdf(image_paths, pdf_path)

    with open(pdf_path, 'rb') as f:
        await update.message.reply_document(
            document=InputFile(f, filename=filename),
            caption=f"Here's your chapter: {title}"
        )


async def list_chapters(update: Update, context: ContextTypes.DEFAULT_TYPE, page=1):
    data = get_json()

    # --- Sorting preference ---
    sort_mode = "chapter"
    for arg in context.args:
        if arg.startswith("sort="):
            sort_mode = arg.split("=")[1].strip()

    context.user_data["sort_mode"] = sort_mode

    chapters = data.get("chapters", {})

    if sort_mode == "chapter":
        # Sort by chapter key (as int)
        all_chapters = sorted(chapters.items(), key=lambda x: float(x[0]), reverse=True)
    else:
        # Default: sort by last_updated timestamp
        all_chapters = sorted(chapters.items(), key=lambda x: x[1].get("last_updated", 0), reverse=True)

    total_pages = (len(all_chapters) + CHAPTERS_PER_PAGE - 1) // CHAPTERS_PER_PAGE
    page = max(1, min(page, total_pages))

    start_index = (page - 1) * CHAPTERS_PER_PAGE
    end_index = start_index + CHAPTERS_PER_PAGE
    page_chapters = all_chapters[start_index:end_index]

    if not page_chapters:
        await update.message.reply_text(f"No chapters found for page {page}.", parse_mode="HTML")
        return

    context.user_data["chapter_refs"] = page_chapters
    context.user_data["current_page"] = page
    context.user_data["list_owner_id"] = update.effective_user.id

    message = f"<b>📚 Chapters (Page {page}/{total_pages})</b>\n\n"
    for idx, (chap_id, chap_data) in enumerate(page_chapters):
        title = escape(chap_data.get("title", "Untitled"))
        ts = chap_data.get("last_updated")
        formatted_time = (
            datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
            if ts else "unknown"
        )
        message += f"<b>{idx + 1}.</b> {title} <i>(⏱️ {formatted_time})</i>\n"

    message += "\nUse <code>/get &lt;number&gt;</code> to download a chapter."
    message += f"\n\n<code>/list sort=chapter</code> or <code>/list sort=updated</code>"

    # --- Inline buttons ---
    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton("« Prev", callback_data=f"list_page:{page - 1}:{sort_mode}"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton("Next »", callback_data=f"list_page:{page + 1}:{sort_mode}"))

    keyboard = InlineKeyboardMarkup([buttons]) if buttons else None

    await update.message.reply_text(message, parse_mode="HTML", reply_markup=keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "<b>🤖 Available Commands</b>\n\n"
        "<b>/list</b> — Show the latest chapters (sorted by last updated)\n"
        "Usage: <code>/list</code>\n\n"
        "<b>/list sort=chapter</b> — Show chapters sorted by chapter number\n"
        "Usage: <code>/list sort=chapter</code>\n\n"
        "<b>/get &lt;number&gt;</b> — Download a chapter from the last listed page\n"
        "Example: <code>/get 1</code> (gets the first chapter from the current list)\n\n"
        "<b>🔄 Pagination:</b>\n"
        "Use the inline buttons <b>« Prev</b> and <b>Next »</b> to scroll through chapters.\n"
        "Sorting will persist as you navigate.\n\n"
        "<b>ℹ️ Tip:</b> Always use <code>/list</code> before <code>/get</code> to refresh your chapter list."
    )

    await update.message.reply_text(message, parse_mode="HTML")
