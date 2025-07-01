import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

url = "https://fa3777315fb68c.lhr.life"  # URL фронта

load_dotenv()

# Telegram Bot Token (set in environment variable or hardcode for testing)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Handler for /goals command
@dp.message(Command("goals"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть Mini App", web_app=types.WebAppInfo(url=url))]
    ])
    await message.reply("Откройте Mini App:", reply_markup=keyboard)

# Main function to run the bot
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())