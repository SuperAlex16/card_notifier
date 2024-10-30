import os

import telebot
import schedule
import threading
import time

from dotenv import load_dotenv
from handlers import register_handlers
from functions import safe_polling, send_reminders
from db_functions import init_db
from logger import logging
from settings import reminder_period

load_dotenv()

# Получение токена и chat_id из переменных окружения
token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('CHAT_ID')

if not token or not chat_id:
    logging.error('Токен или chat_id не установлен в файле .env.')
    raise ValueError('Необходимые переменные окружения не установлены.')

chat_id = int(chat_id)

init_db()


# Функция для запуска планировщика
def run_scheduler_with_reminders():
    schedule.every(1).minutes.do(send_reminders)
    while True:
        schedule.run_pending()
        time.sleep(reminder_period)


def main():
    bot = telebot.TeleBot(token)
    logging.info(f'Создан экземпляр бота: {bot}')
    register_handlers(bot)

    bot_thread = threading.Thread(target=safe_polling, args=(bot,), daemon=True)
    bot_thread.start()
    logging.info(f'Бот запущен в thread: {bot_thread.ident}')

    scheduler_thread = threading.Thread(target=run_scheduler_with_reminders, daemon=True)
    scheduler_thread.start()
    logging.info(f'Планировщик запущен в thread: {scheduler_thread.ident}')

    while True:
        time.sleep(60)


if __name__ == '__main__':
    main()
