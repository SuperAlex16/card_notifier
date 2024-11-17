import os
import sys
import telebot
import time

from dotenv import load_dotenv
from handlers import register_handlers
from logger import logging

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")

if not token:
	logging.error("No valid token in .env")
	sys.exit("End process: environment variable not found")


def main(bot):
	register_handlers(bot)

	while True:
		try:
			logging.info(f"Start bot.polling: {bot}")
			bot.polling(non_stop=True, interval=0, timeout=20)
		except Exception as e:
			logging.error(f"Error: {e}")
			if isinstance(e, telebot.apihelper.ApiException) and e.error_code == 403:
				logging.error("Bot was blocked by user")
			logging.info("Restarting bot in 5 seconds...")
			logging.exception("Stack trace of the exception")
			time.sleep(5)


if __name__ == '__main__':
	bot = telebot.TeleBot(token)
	logging.info(f"Bot is created: {bot}")
	main(bot)
