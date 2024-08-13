from app.transcribe import bot
import os

chat_id = os.getenv("TELEGRAM_CHAT_ID")

async def send_feedback(text):
  async with bot:
    await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")

async def send_audio(file):
  async with bot:
    file.seek(0)
    await bot.send_document(chat_id=chat_id, document=file)

