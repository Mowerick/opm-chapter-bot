from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.config import CHAPTERS_PER_PAGE
from src.services.chapter_service import get_json
from html import escape
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        _, page_str, sort_mode = query.data.split(":")
        page = int(page_str)
        sort_mode = sort_mode.strip()
        context.user_data["sort_mode"] = sort_mode  # Persist sort preference

        data = get_json()
        chapters = data.get("chapters", {})

        # Sort chapters based on selected mode
        if sort_mode == "chapter":
            all_chapters = sorted(chapters.items(), key=lambda x: float(x[0]), reverse=True)
        else:
            all_chapters = sorted(chapters.items(), key=lambda x: x[1].get("last_updated", 0), reverse=True)

        total_pages = (len(all_chapters) + CHAPTERS_PER_PAGE - 1) // CHAPTERS_PER_PAGE
        page = max(1, min(page, total_pages))
        start = (page - 1) * CHAPTERS_PER_PAGE
        end = start + CHAPTERS_PER_PAGE
        page_chapters = all_chapters[start:end]

        context.user_data["chapter_refs"] = page_chapters
        context.user_data["current_page"] = page

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

        # Inline buttons with preserved sort mode
        buttons = []
        if page > 1:
            buttons.append(InlineKeyboardButton("« Prev", callback_data=f"list_page:{page-1}:{sort_mode}"))
        if page < total_pages:
            buttons.append(InlineKeyboardButton("Next »", callback_data=f"list_page:{page+1}:{sort_mode}"))

        keyboard = InlineKeyboardMarkup([buttons]) if buttons else None

        await query.edit_message_text(message, parse_mode="HTML", reply_markup=keyboard)

    except Exception as e:
        logger.exception(f"Error during pagination: {e}")
        await query.edit_message_text("An error occurred. Please try again.")
