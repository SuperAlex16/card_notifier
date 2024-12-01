import schedule
import threading
import time

from db_functions import get_db_connection
from functions import send_reminders
from logger import logging
from settings import reminder_period


def get_active_id_to_remind():
    conn = get_db_connection()
    cursor = conn.cursor()
    with conn:
        cursor.execute(
            f"""
                        SELECT name 
                        FROM sqlite_master 
                        WHERE type='table';
                        """
        )
        tables = cursor.fetchall()
    active_id_list = [table[0] for table in tables]
    return active_id_list


def run_reminders(bot):
    active_chats = get_active_id_to_remind()
    for chat_id in active_chats:
        scheduler_thread = threading.Thread(
            target=run_scheduler_with_reminders, args=(bot, chat_id), daemon=True
        )
        scheduler_thread.start()
        logging.info(f"run_reminders for {chat_id} started in thread: {scheduler_thread.ident}")


def run_scheduler_with_reminders(bot, chat_id):
    send_reminders(bot, chat_id)
    schedule.every(1).minutes.do(lambda: send_reminders(bot, chat_id))
    while True:
        schedule.run_pending()
        time.sleep(reminder_period)
