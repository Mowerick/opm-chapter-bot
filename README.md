# OPM-Scraper

**OPM-Scraper** is a Python bot that fetches the latest chapters of the *One Punch Man* manga from a public JSON feed. It downloads chapter images, compresses them, converts them into a PDF, and sends the PDF to a Telegram chat or channel. You can also interact with the bot using commands like `/list` and `/get`.

---

## Features

- Periodically checks for new *One Punch Man* chapters (every **30 minutes**).
- Downloads and compresses images using `Pillow`.
- Converts images into PDFs with `img2pdf`.
- Sends new chapter PDFs to a configured Telegram chat/channel.
- Interactive Telegram bot commands:
  - `/list` chapters with inline pagination buttons.
  - `/list sort=chapter` to sort chapters numerically.
  - `/get <number>` to download a chapter from the most recent `/list`.
  - `/help` command with nicely formatted usage instructions.
- Inline buttons (`« Prev` / `Next »`) for chapter browsing.
- Caches generated PDFs to avoid re-downloading chapters.
- User-specific command context (each Telegram user sees their own `/list` state).

---

## Shoutout

Special thanks to [@funkyhippo](https://gist.github.com/funkyhippo) for maintaining the public JSON feed that powers this bot:  
[`https://gist.githubusercontent.com/funkyhippo/1d40bd5dae11e03a6af20e5a9a030d81/raw`](https://gist.githubusercontent.com/funkyhippo/1d40bd5dae11e03a6af20e5a9a030d81/raw)


---

## Requirements

Install Python dependencies with:

```bash
pip install -r requirements.txt
```

### `requirements.txt` content:
```text
python-telegram-bot
requests 
Pillow 
img2pdf 
beautifulsoup4
python-dotenv
logging
asyncio
```

---

## Environment Setup

Create a `.env` file in your root directory with:

```env
BOT_TOKEN=your_telegram_bot_token
CHAT_ID=your_chat_or_channel_id
JSON_URL=https://gist.githubusercontent.com/funkyhippo/1d40bd5dae11e03a6af20e5a9a030d81/raw
```

- Get a `BOT_TOKEN` via [@BotFather](https://t.me/BotFather).
- Get your `CHAT_ID` by messaging your bot and inspecting `update.message.chat.id`.

---

## Usage

Start the bot with:

```bash
python opm_scraper.py
```

The script will:

1. Check for new chapters every 15 minutes.
2. If a new chapter is found:
   - Images are downloaded and compressed.
   - A PDF is generated and cached.
   - The PDF is sent via Telegram.
   - Temporary images are deleted.

---

## Telegram Commands

```text
/list
```
Show the latest chapters (default: sorted by `chapter`).

```text
/list sort=updated
```
Sort chapters numerically by chapter number (descending).

```text
/get <number>
```
Download the chapter from the most recently listed page (e.g., `/get 1` for the first).

```text
/help
```
Displays a list of available commands and how to use them.

### Pagination
After running `/list`, use the inline buttons:
- `« Prev` / `Next »` to flip pages.
- Sorting mode persists across page flips.

---

## Tech Stack

- `python-telegram-bot` — Telegram Bot API wrapper (v20+)
- `img2pdf` — Lightweight PDF generation from images
- `Pillow` — Image compression and manipulation
- `dotenv` — Load environment variables from `.env`

---

## Resources

- [python-telegram-bot Docs](https://docs.python-telegram-bot.org/)
- [Telegram Bot API Reference](https://core.telegram.org/bots/api)

---

## Disclaimer

This project is intended for **educational purposes only**. It fetches data from publicly available sources. Please respect the rights of manga creators and publishers.
