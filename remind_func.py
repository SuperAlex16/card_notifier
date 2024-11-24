import schedule
import threading
import time

from functions import send_reminders
from logger import logging
from settings import reminder_period


def run_reminders(bot, chat_id):
    scheduler_thread = threading.Thread(target=run_scheduler_with_reminders, args=(bot, chat_id), daemon=True)
    scheduler_thread.start()
    logging.info(f'Планировщик запущен в thread: {scheduler_thread.ident}')


def run_scheduler_with_reminders(bot, chat_id):
    schedule.every(1).minutes.do(lambda: send_reminders(bot, chat_id))
    while True:
        schedule.run_pending()
        time.sleep(reminder_period)
