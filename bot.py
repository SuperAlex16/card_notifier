import os
import telebot
import schedule
import threading
import time

from dotenv import load_dotenv
from handlers import register_handlers
from functions import send_reminders
from logger import logging
from settings import reminder_period

load_dotenv()

# Получение токена и chat_id из переменных окружения
token = os.getenv('TELEGRAM_BOT_TOKEN')
# chat_id = os.getenv('CHAT_ID')

if not token:
    logging.error('Токен не установлен в файле .env.')
    raise ValueError('Необходимые переменные окружения не установлены.')


# chat_id = int(chat_id)


def main(bot):

    logging.info(f'Создан экземпляр бота: {bot}')
    register_handlers(bot)

    while True:
        try:
            logging.info(f"Запущен bot.polling: {bot}")
            bot.polling(non_stop=True, interval=0, timeout=20)
        except Exception as e:
            logging.error(f"Ошибка: {e}")  # Логируем ошибку
            if isinstance(e, telebot.apihelper.ApiException) and e.error_code == 403:
                logging.error("Бот был заблокирован пользователем.")
            logging.info("Перезапуск бота через 5 секунд...")
            logging.exception("Трассировка стека исключения:")
            time.sleep(5)


if __name__ == '__main__':
    bot = telebot.TeleBot(token)
    main(bot)
