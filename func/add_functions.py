from datetime import datetime

from dateutil.relativedelta import relativedelta

from func.db_functions import get_db_connection
from keyboards import cards_list_keyboard, create_calendar, recurrence_type_keyboard, \
    transactions_type_keyboard
from log.logger import logging
from settings import recurrent_count_months
from func.utils import create_uuid


# add transaction
def start_addition_process(bot, chat_id):
    ask_for_transaction_date(bot, chat_id)


def ask_for_transaction_date(bot, chat_id):
    markup = create_calendar()
    bot.send_message(chat_id, "Выберите дату:", reply_markup=markup)


def ask_for_card_name(bot, chat_id):
    markup = cards_list_keyboard(chat_id)
    bot.send_message(chat_id, "Выберите карту из списка или добавьте новую:", reply_markup=markup)


def ask_for_transaction_type(bot, chat_id):
    markup = transactions_type_keyboard()
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)


def ask_for_amount(bot, chat_id):
    bot.send_message(chat_id, "Введите сумму:")


def ask_for_monthly_recurrence(bot, chat_id):
    markup = recurrence_type_keyboard()
    bot.send_message(chat_id, "Повторять ежемесячно?", reply_markup=markup)


def save_transactions_to_db(chat_id, transaction_dict, payment_uuid):
    data = transaction_dict

    table_name = chat_id

    date_obj = datetime(
        year=data[chat_id]['date']['year'],
        month=data[chat_id]['date']['month'],
        day=data[chat_id]['date']['day']
    )
    date = date_obj.date().isoformat()

    card_name = data[chat_id]['card']
    transaction_type = data[chat_id]['type']
    amount = data[chat_id]['amount']
    recurrence_id = data[chat_id]['recurrence_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if recurrence_id is None:
            cursor.execute(
                f"""
                INSERT INTO '{table_name}' (uuid, date, card_name, transaction_type, amount, execution_status,
                recurrence_id, is_active)
                VALUES (?, ?, ?, ?, ?, 0, ?, 1)
                """, (payment_uuid, date, card_name, transaction_type, amount, recurrence_id)
            )
            logging.info(f"Single transaction {payment_uuid} was saved")
        else:
            # Множественные транзакции (рекуррентные)
            recurrenced_date = date_obj
            for _ in range(recurrent_count_months):
                payment_uuid = create_uuid()
                cursor.execute(
                    f"""
                    INSERT INTO '{table_name}' (uuid, date, card_name, transaction_type, amount, execution_status,
                    recurrence_id, is_active)
                    VALUES (?, ?, ?, ?, ?, 0, ?, 1)
                    """,
                    (payment_uuid, recurrenced_date.date().isoformat(), card_name, transaction_type, amount,
                     recurrence_id)
                )

                recurrenced_date += relativedelta(months=1)
            logging.info(
                f"Recurrent transactions with {recurrence_id} were saved"
            )
        conn.commit()
    except Exception as e:
        logging.error(f"Error saving transactions: {e}")
        conn.rollback()
    finally:
        conn.close()
        del transaction_dict[chat_id]


def undo_save_transactions_to_db(chat_id, action_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    table_name = chat_id
    try:
        cursor.execute(
            f"""DELETE FROM "{table_name}"
            WHERE "UUID" = ? OR "recurrence_id" = ?
        """, (action_id, action_id)
        )
        conn.commit()
    except Exception as e:
        logging.error(f"Error undoing transactions: {e}")
    finally:
        conn.close()
