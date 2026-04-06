import asyncio
import json
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from utils.meme_generator import MemeGenerator

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

meme_gen = MemeGenerator()

# Load templates
with open("templates.json", "r") as f:
    TEMPLATES = json.load(f)["templates"]

template_map = {t["id"]: t for t in TEMPLATES}
current_user_template = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🤖 **Meme Generator Bot** is ready!\n\n"
        "Use /meme to create a meme.\n"
        "You can send text with `|` to separate top and bottom text.",
        parse_mode="Markdown"
    )

@dp.message(Command("meme"))
async def show_meme_templates(message: types.Message):
    keyboard = []
    for template in TEMPLATES:
        keyboard.append([InlineKeyboardButton(
            text=template["name"], 
            callback_data=f"temp:{template['id']}"
        )])
    
    await message.answer(
        "🎨 **Choose a meme template:**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("temp:"))
async def select_template(callback: types.CallbackQuery):
    template_id = callback.data.split(":")[1]
    current_user_template[callback.from_user.id] = template_id
    
    template = template_map.get(template_id)
    
    await callback.message.edit_text(
        f"✅ **Selected:** {template['name']}\n\n"
        "Now send your meme text.\n"
        "You can use `|` to separate top and bottom text.\n\n"
        "Example: `When you see the code|But it works`"
    )
    await callback.answer()

@dp.message(F.text)
async def generate_meme(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if user_id not in current_user_template:
        await message.answer("Please use /meme first to choose a template.")
        return
    
    template_id = current_user_template[user_id]
    template = template_map.get(template_id)
    
    if not template:
        await message.answer("Template not found.")
        return
    
    template_path = f"templates/{template['file']}"
    output_path = f"memes/meme_{user_id}.jpg"
    
    os.makedirs("memes", exist_ok=True)
    
    top_text = text
    bottom_text = ""
    
    if "|" in text:
        parts = [p.strip() for p in text.split("|", 1)]
        top_text = parts[0]
        if len(parts) > 1:
            bottom_text = parts[1]
    
    try:
        meme_gen.create_meme(
            template_path=template_path,
            top_text=top_text,
            bottom_text=bottom_text,
            output_path=output_path
        )
        
        await message.answer_photo(
            FSInputFile(output_path),
            caption=f"🎉 Your meme is ready!\nTemplate: {template['name']}"
        )
    except Exception as e:
        await message.answer(f"❌ Error generating meme: {str(e)}")

async def main():
    print("🚀 Meme Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
