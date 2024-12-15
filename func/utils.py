import uuid

from func.db_functions import get_db_connection
from settings import main_menu_keyboard_text


def create_uuid():
    result = str(uuid.uuid4())
    return result


def get_weekday_short(date):
    weekdays = {
        0: 'пн.',
        1: 'вт.',
        2: 'ср.',
        3: 'чт.',
        4: 'пт.',
        5: 'сб.',
        6: 'вс.'
    }
    return weekdays.get(date.weekday(), '')


def is_recurrence(chat_id, payment_uuid):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""
			SELECT recurrence_id 
			FROM transactions
			WHERE user_id = ? AND UUID = ?
			""", (chat_id, payment_uuid,)
        )
        result = cursor.fetchone()
    finally:
        conn.close()
    recurrence_id = result["recurrence_id"]
    return recurrence_id if result else None


def create_transactions_dict(chat_id, key, value, transaction_dict):
    if chat_id not in transaction_dict:
        transaction_dict[chat_id] = {}

    transaction_dict[chat_id][key] = value
    return transaction_dict


def exit_current_action(bot, chat_id, message, user_states):
    if message in main_menu_keyboard_text.values():
        user_states.pop(chat_id, None)
        bot.send_message(chat_id, "Вы вышли из текущего действия. Пожалуйста, выберите опцию из меню.")
        return True
    return False
