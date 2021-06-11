from telegram.ext import Updater
import logging

from config import *


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

updater = Updater(TELEGRAM_TOKEN)


def send_message(message):
    updater.dispatcher.bot.sendMessage(chat_id=TELEGRAM_CHAT_ID, text=message)
