from datetime import datetime, timedelta
from telebot import types

from func.db_functions import get_db_connection
from keyboards import transaction_info_keyboard
from log.logger import logging
from settings import db_transaction_types
from func.utils import get_weekday_short


def show_today(message, bot, chat_id):
    current_date = datetime.now().date().isoformat()  # Форматируем в 'YYYY-MM-DD'
    payments_today = get_transactions_by_date(current_date, chat_id)

    if payments_today:
        for payment in payments_today:
            weekday_short = get_weekday_short(
                datetime.strptime(
                    payment['date'].split()[0], '%Y-%m-%d'
                ).date()
            )
            date_obj = datetime.strptime(payment['date'].split()[0], '%Y-%m-%d')

            formatted_date = date_obj.strftime('%d/%m/%Y')
            payment_str = (f"{formatted_date} ({weekday_short}),"
                           f" {payment['card_name']},"
                           f" {payment['transaction_type']}"
                           f" {payment['amount']:,.2f} руб.")
            payment_uuid = payment['uuid']

            markup = transaction_info_keyboard(payment_uuid)
            bot.send_message(message.chat.id, payment_str, reply_markup=markup)
        logging.info(f"Отправлены транзакции на сегодня пользователю {message.chat.id}.")
    else:
        bot.send_message(message.chat.id, "Нет транзакций на сегодня. Можно расслабиться 😌")
        logging.info(f"Транзакций на сегодня нет. Информация отправлена пользователю {message.chat.id}.")


def show_nearest_days(message, days, bot):
    current_date = datetime.now().date()
    date_limit = (current_date + timedelta(days=days)).isoformat()
    payments = get_transactions_in_date_range(current_date.isoformat(), date_limit, message)

    if payments:
        for payment in payments:
            weekday_short = get_weekday_short(
                datetime.strptime(
                    payment['date'].split()[0], '%Y-%m-%d'
                ).date()
            )
            payment_str = f'{payment['date']} ({weekday_short}), {payment['card_name']}, {payment['transaction_type']} {payment['amount']:,.2f} руб.'
            markup = types.InlineKeyboardMarkup()

            # Кнопки для выполнения, редактирования и удаления
            done_button = types.InlineKeyboardButton('✅', callback_data=f'done_{payment['uuid']}')
            edit_button = types.InlineKeyboardButton('✏️', callback_data=f'edit_{payment['uuid']}')
            delete_button = types.InlineKeyboardButton('🗑️', callback_data=f'delete_{payment['uuid']}')
            markup.add(done_button, edit_button, delete_button)

            bot.send_message(message.chat.id, payment_str, reply_markup=markup)
        logging.info(f'Отправлены транзакции за следующие {days} дней пользователю {message.chat.id}.')
    else:
        bot.send_message(message.chat.id, f'Нет транзакций в течение следующих {days} дней 😸')
        logging.info(
            f'Транзакций за следующие {days} дней нет. Информация отправлена пользователю {message.chat.id}.'
        )


def show_this_month(message, bot, chat_id):
    current_date = datetime.now().date()
    start_of_month = current_date.replace(day=1).isoformat()  # Первый день текущего месяца
    end_of_month = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    end_of_month = end_of_month.isoformat()  # Последний день текущего месяца

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
            SELECT * FROM '{chat_id}'
            WHERE date BETWEEN ? AND ? AND date >= ? AND execution_status = 0 AND is_active = 1
            ORDER BY date, transaction_type = 'снять'
        """, (start_of_month, end_of_month, current_date.isoformat())
    )
    transactions = cursor.fetchall()
    conn.close()

    if transactions:
        for payment in transactions:
            weekday_short = get_weekday_short(datetime.strptime(payment['date'], '%Y-%m-%d').date())
            payment_str = f'{payment['date']} ({weekday_short}), {payment['card_name']}, {payment['transaction_type']} {payment['amount']:,.2f} руб.'
            markup = types.InlineKeyboardMarkup()

            # Кнопки для выполнения, редактирования и удаления
            done_button = types.InlineKeyboardButton('✅', callback_data=f'done_{payment['uuid']}')
            edit_button = types.InlineKeyboardButton('✏️', callback_data=f'edit_{payment['uuid']}')
            delete_button = types.InlineKeyboardButton('🗑️', callback_data=f'delete_{payment['uuid']}')
            markup.add(done_button, edit_button, delete_button)

            bot.send_message(message.chat.id, payment_str, reply_markup=markup)
        logging.info(f'Отправлены предстоящие транзакции за текущий месяц пользователю {message.chat.id}.')
    else:
        bot.send_message(message.chat.id, 'Нет предстоящих транзакций в текущем месяце 😸')
        logging.info(
            f'Предстоящих транзакций на текущий месяц нет. Информация отправлена пользователю {message.chat.id}.'
        )


def get_transactions_by_date(date, chat_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    transaction_type_1 = db_transaction_types[1]
    transaction_type_2 = db_transaction_types[2]

    cursor.execute(
        f"""
        SELECT * FROM "{chat_id}"
        WHERE date = ? 
            AND execution_status = 0 
            AND is_active = 1
        ORDER BY date,
        CASE 
            WHEN transaction_type = ? THEN 1
            WHEN transaction_type = ? THEN 2
        END
        """, (date, transaction_type_1, transaction_type_2)
    )

    transactions = cursor.fetchall()
    conn.close()
    return transactions


def delete_transactions(chat_id, payment_id=None, recurrence_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if recurrence_id:
            cursor.execute(
                f"""
                        UPDATE '{chat_id}' 
                        SET is_active = 0 
                        WHERE recurrence_id = ?
                        """, (recurrence_id,)
            )
            conn.commit()

        elif payment_id:
            cursor.execute(
                f"""
                        UPDATE '{chat_id}' 
                        SET is_active = 0 
                        WHERE UUID = ?
                        """, (payment_id,)
            )
            conn.commit()
    except Exception as e:
        logging.error(f"{e}")
    finally:
        conn.close()


def undo_delete_transactions(chat_id, payment_id=None, recurrence_id=None, ):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if recurrence_id:
            cursor.execute(
                f"""
                        UPDATE '{chat_id}' 
                        SET is_active = 1 
                        WHERE recurrence_id = ?
                        """, (recurrence_id,)
            )
            conn.commit()

        elif payment_id:
            cursor.execute(
                f"""
                        UPDATE '{chat_id}' 
                        SET is_active = 1 
                        WHERE UUID = ?
                        """, (payment_id,)
            )
            conn.commit()
    except Exception as e:
        logging.error(f"{e}")
    finally:
        conn.close()


def done_transactions(chat_id, payment_uuid=None, recurrence_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if recurrence_id:
            cursor.execute(
                f"""
                            UPDATE '{chat_id}' 
                            SET execution_status = 1, is_active = 0
                            WHERE recurrence_id = ?
                            """, (recurrence_id,)
            )
            conn.commit()

        elif payment_uuid:
            cursor.execute(
                f"""
                            UPDATE '{chat_id}' 
                            SET execution_status = 1, is_active = 0 
                            WHERE UUID = ?
                            """, (payment_uuid,)
            )
            conn.commit()
    except Exception as e:
        logging.error(f"{e}")
    finally:
        conn.close()


def undone_transactions(chat_id, payment_uuid=None, recurrence_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if recurrence_id:
            cursor.execute(
                f"""
                            UPDATE '{chat_id}' 
                            SET execution_status = 0, is_active = 1
                            WHERE recurrence_id = ?
                            """, (recurrence_id,)
            )
            conn.commit()

        elif payment_uuid:
            cursor.execute(
                f"""
                            UPDATE '{chat_id}' 
                            SET execution_status = 0, is_active = 1
                            WHERE UUID = ?
                            """, (payment_uuid,)
            )
            conn.commit()
    except Exception as e:
        logging.error(f"{e}")
    finally:
        conn.close()


def get_transactions_in_date_range(start_date, end_date, message):
    chat_id = message.chat.id
    transaction_type_1 = db_transaction_types[1]
    transaction_type_2 = db_transaction_types[2]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
                SELECT * FROM '{chat_id}'
                WHERE date BETWEEN ? AND ? 
                    AND execution_status = 0
                    AND is_active = 1
                ORDER BY date,
                CASE
                    WHEN transaction_type = ? THEN 1
                    WHEN transaction_type = ? THEN 2
                END   
                """, (start_date, end_date, transaction_type_1, transaction_type_2)
    )
    transactions = cursor.fetchall()
    conn.close()
    return transactions
