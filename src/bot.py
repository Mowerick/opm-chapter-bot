from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN
from handlers.commands import list_chapters, get_chapter, help_command
from handlers.callbacks import handle_pagination
from services.poller import on_startup
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("chapter_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("list", list_chapters))
    app.add_handler(CommandHandler("get", get_chapter))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(handle_pagination))
    app.post_init = on_startup
    logger.info("Bot is starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
