import os
import sys
import telebot
import time

from dotenv import load_dotenv
from handlers import register_handlers
from logger import logging

load_dotenv()

token = os.getenv('TELEGRAM_BOT_TOKEN')

if not token:
    logging.error('Токен не установлен в файле .env.')
    sys.exit("Завершение выполнения: переменные окружения не установлены.")


def main(bot):
    register_handlers(bot)

    while True:
        try:
            logging.info(f"Запущен bot.polling: {bot}")
            bot.polling(non_stop=True, interval=0, timeout=20)
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            if isinstance(e, telebot.apihelper.ApiException) and e.error_code == 403:
                logging.error("Бот был заблокирован пользователем.")
            logging.info("Перезапуск бота через 5 секунд...")
            logging.exception("Трассировка стека исключения:")
            time.sleep(5)


if __name__ == '__main__':
    bot = telebot.TeleBot(token)
    logging.info(f'Создан экземпляр бота: {bot}')
    main(bot)
