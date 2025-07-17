# OPM-Scraper

**OPM-Scraper** is a Python script that periodically checks for new chapters of the *One Punch Man* manga from a JSON feed. It downloads the latest chapter's images, compresses them, bundles them into a PDF, and automatically sends the PDF to a Telegram channel or chat.

---

## Features

- Fetches latest chapter metadata from a public JSON source.
- Downloads and compresses chapter images using `Pillow`.
- Converts the images into a PDF using `img2pdf`.
- Sends the final PDF to a Telegram chat/channel using `python-telegram-bot`.
- Automatically deletes the downloaded images after use.
- Checks for updates every **15 minutes**.

---

## Folder Structure

```
.
├── chapter_bot.log          # Log file for script activity
├── last_seen_chapter.txt    # Tracks last downloaded chapter
├── images/                  # Temporary folder for downloaded images
├── opm_chapters/            # Output folder for generated PDFs
├── .env                     # Environment variables (Telegram credentials)
└── opm_scraper.py           # Main script
```

---

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

### `requirements.txt` content:
```text
requests
img2pdf
python-dotenv
pillow
python-telegram-bot==20.0
```

> Note: `python-telegram-bot` v20+ uses asyncio. This script is compatible.

---

## Environment Variables

Create a `.env` file in the root directory with the following contents:

```env
BOT_TOKEN=your_telegram_bot_token
CHAT_ID=your_chat_or_channel_id
```

- To get a bot token: use [@BotFather](https://t.me/BotFather) on Telegram.
- To find your `CHAT_ID`, you can message your bot and inspect the `chat.id` using a script or a Telegram API bot.

---

## Usage

Run the script:

```bash
python opm_scraper.py
```

The script will run indefinitely, checking for new chapters every 15 minutes (900 seconds). When a new chapter is found:
1. Images are downloaded and compressed.
2. A PDF is created.
3. The PDF is sent to the configured Telegram destination.
4. Images are deleted after conversion.

---

## Telegram Bot Docs

This script uses [`python-telegram-bot`](https://pytba.readthedocs.io/en/latest/) v20+. For advanced usage, see their official documentation.

## Disclaimer

This script is for **educational purposes only**. All content is sourced from publicly available JSON feeds. Please respect the rights of the content creators and publishers.
