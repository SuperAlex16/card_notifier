import uuid

from func.db_functions import get_db_connection


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
			FROM '{chat_id}'
			WHERE UUID = ?
			""", (payment_uuid,)
        )
        result = cursor.fetchone()
    finally:
        conn.close()
    # print(f"is_recurrence: {result.keys()}")
    recurrence_id = result["recurrence_id"]
    return recurrence_id if result else None


def create_transactions_dict(chat_id, key, value, transaction_dict):
    if chat_id not in transaction_dict:
        transaction_dict[chat_id] = {}

    transaction_dict[chat_id][key] = value
    return transaction_dict
