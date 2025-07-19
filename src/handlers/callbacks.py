from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.config import CHAPTERS_PER_PAGE
from src.services.chapter_service import get_json
from html import escape
from datetime import datetime
import logging
import telegram
import time

logger = logging.getLogger(__name__)

def keyboards_equal(kb1, kb2):
    return (kb1.to_dict() if kb1 else None) == (kb2.to_dict() if kb2 else None)

async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    now = time.time()

    # Restrict access to owner
    if context.user_data.get("list_owner_id") != user_id:
        await query.answer("This list belongs to someone else.", show_alert=True)
        return

    # Flood lock
    flood_until = context.user_data.get("flood_locked_until", 0)
    if flood_until > now:
        retry_after = int(flood_until - now)
        await query.answer(f"You're doing that too fast! Please wait {retry_after} seconds.", show_alert=True)
        return

    # Click cooldown
    last_click = context.user_data.get("last_pagination_time", 0)
    if now - last_click < 1.0:
        await query.answer("Please wait a moment before clicking again.", show_alert=True)
        return
    context.user_data["last_pagination_time"] = now

    # Ongoing operation guard
    if context.user_data.get("pagination_busy"):
        await query.answer("Still loading the previous page. Please wait.", show_alert=True)
        return

    try:
        context.user_data["pagination_busy"] = True

        # Save current markup in case we need to restore it later
        context.user_data["last_keyboard"] = query.message.reply_markup

        # Show loading state
        loading_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("⏳ Loading...", callback_data="noop")]
        ])

        if not keyboards_equal(query.message.reply_markup, loading_markup):
            try:
                await query.edit_message_reply_markup(reply_markup=loading_markup)
            except telegram.error.BadRequest as e:
                if "Message is not modified" not in str(e):
                    logger.warning(f"Failed to set loading state: {e}")

        # Parse callback data
        _, page_str, sort_mode = query.data.split(":")
        page = int(page_str)
        sort_mode = sort_mode.strip()
        context.user_data["sort_mode"] = sort_mode

        # Load and sort chapters
        data = get_json()
        chapters = data.get("chapters", {})

        if sort_mode == "release":
            all_chapters = sorted(chapters.items(), key=lambda x: x[1].get("last_updated", 0), reverse=True)
        else:
            all_chapters = sorted(chapters.items(), key=lambda x: float(x[0]), reverse=True)

        total_pages = (len(all_chapters) + CHAPTERS_PER_PAGE - 1) // CHAPTERS_PER_PAGE
        page = max(1, min(page, total_pages))
        start = (page - 1) * CHAPTERS_PER_PAGE
        end = start + CHAPTERS_PER_PAGE
        page_chapters = all_chapters[start:end]

        context.user_data["chapter_refs"] = page_chapters
        context.user_data["current_page"] = page

        # Build message text
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

        # Pagination buttons
        buttons = []
        if page > 1:
            buttons.append(InlineKeyboardButton("« Prev", callback_data=f"list_page:{page-1}:{sort_mode}"))
        if page < total_pages:
            buttons.append(InlineKeyboardButton("Next »", callback_data=f"list_page:{page+1}:{sort_mode}"))
        keyboard = InlineKeyboardMarkup([buttons]) if buttons else None

        # Avoid redundant edits
        current_text = query.message.text or ""
        if message == current_text and keyboards_equal(query.message.reply_markup, keyboard):
            logger.debug("Skipped update: no change.")
            await query.answer("You're already on this page.", show_alert=True)
            return

        # Update message
        await query.edit_message_text(message, parse_mode="HTML", reply_markup=keyboard)
        context.user_data.pop("last_keyboard", None)  # clear saved keyboard after success

    except telegram.error.RetryAfter as e:
        logger.warning(f"Flood control exceeded. Retry in {e.retry_after} seconds")
        context.user_data["flood_locked_until"] = time.time() + e.retry_after
        await query.answer(f"Too many requests. Please wait {e.retry_after} seconds.", show_alert=True)
        try:
            old_markup = context.user_data.get("last_keyboard")
            if old_markup:
                await query.edit_message_reply_markup(reply_markup=old_markup)
        except Exception as restore_err:
            logger.warning(f"Failed to restore previous keyboard: {restore_err}")

    except Exception as e:
        logger.exception(f"Error during pagination: {e}")
        await query.answer("An error occurred. Please try again.", show_alert=True)
        try:
            old_markup = context.user_data.get("last_keyboard")
            if old_markup:
                await query.edit_message_reply_markup(reply_markup=old_markup)
        except Exception as restore_err:
            logger.warning(f"Failed to restore previous keyboard: {restore_err}")

    finally:
        context.user_data["pagination_busy"] = False
