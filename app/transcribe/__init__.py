from flask import Blueprint
from telegram import Bot
import os

api_key = os.getenv('TELEGRAM_API_KEY')

bot = Bot(api_key)
transcribe = Blueprint('transcribe', __name__, template_folder='templates')


from app.transcribe import routes