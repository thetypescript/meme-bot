# Meme Lord 69 🤖🔥

A Telegram meme bot powered by [memegen.link](https://memegen.link).

## Features

- Pick from 10 popular meme templates
- Custom top/bottom text (use `|` to split)
- Random template option
- `/meme` — choose a template
- `/random` — random template
- `/help` — usage info
- `/cancel` — cancel current meme

## Setup

```bash
git clone https://github.com/thetypescript/meme-bot.git
cd meme-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
BOT_TOKEN=your_telegram_bot_token
```

Run:

```bash
python main.py
```

## Built With

- [aiogram 3.x](https://github.com/aiogram/aiogram) — async Telegram bot framework
- [memegen.link](https://memegen.link) — meme image generation API
