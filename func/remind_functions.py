import schedule
import threading
import time

from datetime import datetime, timedelta

from func.db_functions import get_db_connection
from keyboards import send_reminder_keyboard
from log.logger import logging
from settings import db_transaction_types, reminder_period, reminder_today_times, reminder_tomorrow_times


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


def send_reminders(bot, chat_id):
    logging.info('send_reminders запущен')

    transaction_type_1 = db_transaction_types[1]
    transaction_type_2 = db_transaction_types[2]

    current_datetime = datetime.now()
    current_date = current_datetime.date().isoformat()

    current_time_str = current_datetime.time().strftime("%H:%M")

    tomorrow_date = (datetime.fromisoformat(current_date) + timedelta(days=1)).date().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
                SELECT * FROM '{chat_id}'
                WHERE execution_status = 0
                AND is_active = 1
                ORDER BY date,
                CASE 
                    WHEN transaction_type = ? THEN 1
                    WHEN transaction_type = ? THEN 2
                END
                """, (transaction_type_1, transaction_type_2)
    )
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        payment_uuid = row['UUID']
        payment_date = row['date']  # Строка в формате 'YYYY-MM-DD'
        card_name = row['card_name']
        transaction_type = row['transaction_type']
        amount = row['amount']

        # Проверка условий для отправки напоминания на сегодня
        if payment_date == current_date and current_time_str in reminder_today_times:
            logging.info(
                f"Today's reminder: текущее время: {current_time_str}, время напоминания:"
                f" {reminder_today_times}"
            )
            message_text = f"‼️ Братишка, не шути так! Срочно: {amount:,.2f} руб. {transaction_type} по карте {card_name}"
            send_reminder_with_buttons(payment_uuid, message_text, transaction_type, bot, chat_id)

        # Проверка условий для отправки напоминания на завтра
        elif payment_date == tomorrow_date and current_time_str == reminder_tomorrow_times:
            logging.info(
                f"Tomorrow's reminder: текущее время: {current_time_str}, время напоминания:"
                f" {reminder_tomorrow_times}"
            )
            message_text = f"⏰ Не забудь: Завтра {transaction_type} {amount:,.2f} руб. по карте {card_name}"
            send_reminder_with_buttons(payment_uuid, message_text, transaction_type, bot, chat_id)
        else:
            pass


def run_scheduler():
    while True:
        # Выполняем все запланированные задачи
        schedule.run_pending()

        # Определяем, сколько времени до следующего события
        next_run = schedule.idle_seconds()

        if next_run is None:
            # Если нет запланированных задач, делаем паузу на 1 минуту
            time.sleep(60)
        else:
            # Ждем до следующего запланированного события
            time.sleep(max(1, next_run))  # Ставим минимум 1 секунду ожидания


def send_reminder_with_buttons(payment_uuid, message_text, transaction_type, bot, chat_id):
    markup = send_reminder_keyboard(payment_uuid, transaction_type)

    logging.info(f"Отправка напоминания: '{message_text}' с кнопкой для UUID {payment_uuid}")

    try:
        bot.send_message(chat_id, message_text, reply_markup=markup)
        logging.info("Напоминание успешно отправлено.")
    except Exception as e:
        logging.error(f"Ошибка при отправке напоминания: {e}")
