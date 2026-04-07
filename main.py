import asyncio
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

MEME_LORD_NAME = "Meme Lord 69"

TEMPLATES = {
    "drake": "Drake Hotline Bling",
    "distracted": "Distracted Boyfriend",
    "success": "Success Kid",
    "changemymind": "Change My Mind",
    "spongebob": "Mocking SpongeBob",
    "onedoesnot": "One Does Not Simply",
    "fine": "This Is Fine",
    "expandingbrain": "Expanding Brain",
    "womanyelling": "Woman Yelling At Cat",
    "exit12": "Exit 12",
}

# Track user's selected template and text step
user_state = {}  # user_id -> {"template": str, "step": "text"|"confirm"}


def build_template_keyboard():
    keyboard = []
    for key, name in TEMPLATES.items():
        keyboard.append([InlineKeyboardButton(text=name, callback_data=f"tmpl:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_random_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Random Template", callback_data="tmpl:random")]
    ])


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        f"🤖 *{MEME_LORD_NAME}* has arrived!\n\n"
        "Commands:\n"
        "/meme — Pick a template & make a meme\n"
        "/random — Random meme template\n"
        "/help — How to use\n"
        "/cancel — Cancel current meme"
    )


@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        f"*How to use {MEME_LORD_NAME}:*\n\n"
        "1. Send /meme to see templates\n"
        "2. Pick one\n"
        "3. Send your text with `|` to split top/bottom\n"
        "   Example: `Top text|Bottom text`\n"
        "4. Meme gets generated!\n\n"
        "Pro tip: Use `_` for spaces and `~` for formatting in text."
    )


@dp.message(Command("cancel"))
async def cancel(message: types.Message):
    uid = message.from_user.id
    if uid in user_state:
        del user_state[uid]
        await message.answer("❌ Cancelled. Send /meme to start over.")
    else:
        await message.answer("Nothing to cancel. Send /meme to start!")


@dp.message(Command("meme"))
async def show_templates(message: types.Message):
    keyboard = build_template_keyboard()
    await message.answer(
        f"🔥 *{MEME_LORD_NAME}* — Choose your weapon:",
        reply_markup=keyboard
    )


@dp.message(Command("random"))
async def random_meme(message: types.Message):
    import random
    key = random.choice(list(TEMPLATES.keys()))
    user_state[message.from_user.id] = {"template": key}
    name = TEMPLATES[key]
    await message.answer(
        f"🎲 Random pick: *{name}*\n\n"
        "Send your meme text now!\n"
        "Use `|` to separate top and bottom.\n"
        "Example: `Top text|Bottom text`"
    )


@dp.callback_query(F.data.startswith("tmpl:"))
async def handle_template(callback: types.CallbackQuery):
    template = callback.data.split(":")[1]

    if template == "random":
        import random
        template = random.choice(list(TEMPLATES.keys()))

    user_state[callback.from_user.id] = {"template": template}
    name = TEMPLATES.get(template, template)

    try:
        await callback.message.edit_text(
            f"✅ Selected: *{name}*\n\n"
            "Send your meme text now!\n"
            "Use `|` to separate top and bottom.\n"
            "Example: `Top text|Bottom text`"
        )
    except Exception:
        pass  # message already edited (stale callback)

    try:
        await callback.answer()
    except Exception:
        pass


@dp.message(F.text)
async def generate_meme(message: types.Message):
    uid = message.from_user.id

    # Skip if it's a command (handled by Command() filters above)
    if message.text and message.text.startswith("/"):
        return

    if uid not in user_state:
        await message.answer("Send /meme first to pick a template! 🤖")
        return

    template = user_state[uid]["template"]
    text = message.text.strip()

    if not text:
        await message.answer("Send some text! Use `|` to split top/bottom.")
        return

    top = text
    bottom = ""

    if "|" in text:
        parts = [p.strip() for p in text.split("|", 1)]
        top = parts[0] or " "
        bottom = parts[1] if len(parts) > 1 else ""

    from urllib.parse import quote
    import aiohttp
    import tempfile

    top_enc = quote(top)
    bottom_enc = quote(bottom)
    url = f"https://api.memegen.link/images/{template}/{top_enc}/{bottom_enc}.jpg"

    await message.answer("🎨 Cooking your meme...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, allow_redirects=True) as resp:
                if resp.status != 200:
                    raise Exception(f"memegen returned {resp.status}")
                img_data = await resp.read()

        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        tmp.write(img_data)
        tmp.close()

        await message.answer_photo(
            types.FSInputFile(tmp.name, filename="meme.jpg"),
            caption=f"🔥 Delivered by *{MEME_LORD_NAME}*"
        )
        os.unlink(tmp.name)

    except Exception as e:
        logger.error(f"Meme generation failed: {e}")
        # Fallback: try without custom text
        try:
            fallback_url = f"https://api.memegen.link/images/{template}.jpg"
            async with aiohttp.ClientSession() as session:
                async with session.get(fallback_url, allow_redirects=True) as resp:
                    if resp.status != 200:
                        raise Exception(f"fallback returned {resp.status}")
                    img_data = await resp.read()

            tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            tmp.write(img_data)
            tmp.close()

            await message.answer_photo(
                types.FSInputFile(tmp.name, filename="meme.jpg"),
                caption=f"⚠️ Custom text failed, here's the blank template.\nDelivered by *{MEME_LORD_NAME}*"
            )
            os.unlink(tmp.name)
        except Exception as e2:
            logger.error(f"Fallback also failed: {e2}")
            await message.answer("❌ Failed to generate meme. Try different text or another template.")

    # Clean up state
    del user_state[uid]


async def main():
    print(f"🚀 {MEME_LORD_NAME} is now online...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
