import calendar

from datetime import datetime
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from func.db_functions import get_db_connection
from log.logger import logging
from settings import main_menu_keyboard_text, nearest_menu_keyboard_text, db_transaction_types


def start_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = types.KeyboardButton("Начать")
    markup.add(start_button)
    return markup


def main_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton(main_menu_keyboard_text[1])
    btn2 = types.KeyboardButton(main_menu_keyboard_text[2])
    btn3 = types.KeyboardButton(main_menu_keyboard_text[3])
    # btn4 = types.KeyboardButton(main_menu_keyboard_text[4])
    keyboard.add(btn1, btn2)
    keyboard.add(btn3)
    return keyboard


def nearest_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton(nearest_menu_keyboard_text[1])
    btn2 = types.KeyboardButton(nearest_menu_keyboard_text[2])
    btn3 = types.KeyboardButton(nearest_menu_keyboard_text[3])
    btn4 = types.KeyboardButton(nearest_menu_keyboard_text[4])
    back = types.KeyboardButton(nearest_menu_keyboard_text[5])
    keyboard.add(btn1, btn2, btn3, btn4)
    keyboard.add(back)
    return keyboard


def transaction_info_keyboard(payment_uuid):
    markup = types.InlineKeyboardMarkup()

    done_button = types.InlineKeyboardButton('✅', callback_data=f"done_{payment_uuid}")
    edit_button = types.InlineKeyboardButton('✏️', callback_data=f"edit_{payment_uuid}")
    delete_button = types.InlineKeyboardButton('🗑️', callback_data=f"delete_{payment_uuid}")
    markup.add(done_button, edit_button, delete_button)

    return markup


def delete_transactions_keyboard(payment_uuid, recurrence_id):
    logging.info(f"pay: {payment_uuid}, recc: {recurrence_id}")
    markup = types.InlineKeyboardMarkup()
    message = None

    if recurrence_id:
        confirm_button = types.InlineKeyboardButton(
            "Одну", callback_data=f"confirm_delete_{payment_uuid}"
        )
        confirm_series_button = types.InlineKeyboardButton(
            "Серию", callback_data=f"series_delete_{recurrence_id}"
        )
        cancel_button = types.InlineKeyboardButton(
            "Отмена", callback_data="cancel_delete"
        )
        markup.add(confirm_button, confirm_series_button, cancel_button)
        message = "Удалить транзакции?"

    elif recurrence_id is None:
        confirm_button = types.InlineKeyboardButton(
            "Удалить", callback_data=f"confirm_delete_{payment_uuid}"
        )
        cancel_button = types.InlineKeyboardButton(
            "Отмена", callback_data="cancel_delete"
        )
        markup.add(confirm_button, cancel_button)
        message = "Удалить транзакцию?"

    return markup, message


def create_calendar(year=datetime.now().year, month=datetime.now().month):
    markup = InlineKeyboardMarkup()
    markup.row_width = 7

    today = datetime.now()
    is_current_month = (today.year == year and today.month == month)

    markup.add(
        InlineKeyboardButton(f"{calendar.month_name[month]} {year}", callback_data="IGNORE")
    )

    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    markup.add(*[InlineKeyboardButton(day, callback_data="IGNORE") for day in days_of_week])

    cal = calendar.monthcalendar(year, month)
    for week in cal:
        markup.add(
            *[InlineKeyboardButton(
                "---" if day != 0 and (year < today.year or (year == today.year and (month < today.month or (
                    month == today.month and day < today.day)))) else f"{day}" if day != 0 else " ",
                callback_data=f"CALENDAR_DAY_{year}_{month}_{day}" if day != 0 and (year > today.year or (
                    year == today.year and (
                    month > today.month or (month == today.month and day >= today.day)))) else "IGNORE"
                # Запрет выбора прошедших дат
            ) for day in week]
        )

    prev_month = month - 1 if month > 1 else 12
    next_month = month + 1 if month < 12 else 1
    prev_year = year if month > 1 else year - 1
    next_year = year if month < 12 else year + 1

    if month < is_current_month:
        markup.add(
            InlineKeyboardButton("<<", callback_data="IGNORE"),
            InlineKeyboardButton(">>", callback_data=f"CALENDAR_MONTH_{next_year}_{next_month}")
        )
    else:
        markup.add(
            InlineKeyboardButton("<<", callback_data=f"CALENDAR_MONTH_{prev_year}_{prev_month}"),
            InlineKeyboardButton(">>", callback_data=f"CALENDAR_MONTH_{next_year}_{next_month}")
        )

    return markup


def cards_list_keyboard(chat_id):
    def get_card_names(chat_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"""
                            SElECT DISTINCT "card_name" FROM "{chat_id}"
                            """
            )
            unique_card_names = cursor.fetchall()
            return unique_card_names
        except Exception as e:
            logging.error(e)
            return None

    markup = types.InlineKeyboardMarkup()
    cards_list = get_card_names(chat_id)

    if cards_list:
        for card in cards_list:
            card_name = card[0]
            markup.add(
                types.InlineKeyboardButton(
                    text=card_name, callback_data=f"select_card_{card_name}"
                )
            )
    markup.add(
        types.InlineKeyboardButton(
            text="➕ Добавить новую", callback_data=f"add_new_card_"
        )
    )

    return markup


def transactions_type_keyboard():
    markup = types.InlineKeyboardMarkup()

    deposit_button = types.InlineKeyboardButton(
        "⬆️ Внести", callback_data=f"deposit_"

    )
    withdraw_button = types.InlineKeyboardButton(
        "⬇️ Снять", callback_data=f"withdraw_"
    )
    markup.add(deposit_button, withdraw_button)

    return markup


def recurrence_type_keyboard():
    markup = types.InlineKeyboardMarkup()
    recurrence_button = types.InlineKeyboardButton("Да", callback_data="recurrence")
    no_recurrence_button = types.InlineKeyboardButton("Нет", callback_data="no_recurrence")
    markup.add(recurrence_button, no_recurrence_button)

    return markup


def undo_save_transactions_to_db_keyboard(payment_uuid=None, recurrence_id=None):
    markup = types.InlineKeyboardMarkup()
    if payment_uuid is not None:
        undo_add_transactions_button = types.InlineKeyboardButton(
            "❌ Отменить", callback_data=f"undo_add_transactions_{payment_uuid}"
        )
        markup.add(undo_add_transactions_button)
    elif recurrence_id is not None:
        undo_add_transactions_button = types.InlineKeyboardButton(
            "❌ Отменить", callback_data=f"undo_add_transactions_{recurrence_id}"
        )
        markup.add(undo_add_transactions_button)
    return markup


def send_reminder_keyboard(payment_uuid, transaction_type):
    markup = types.InlineKeyboardMarkup()
    if transaction_type == db_transaction_types[1]:
        button = types.InlineKeyboardButton("☑️ Уже внес", callback_data=f"done_{payment_uuid}")
    elif transaction_type == db_transaction_types[2]:
        button = types.InlineKeyboardButton("✅ Уже снял", callback_data=f"withdrawn_{payment_uuid}")
    else:
        button = types.InlineKeyboardButton("✅ Выполнено", callback_data=f"done_{payment_uuid}")
    markup.add(button)
    return markup
