from telebot import types

from logger import logging
from settings import main_menu_keyboard_text, nearest_menu_keyboard_text


def start_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = types.KeyboardButton("Начать")
    markup.add(start_button)
    return markup


# Функция для создания клавиатуры главного меню
def main_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton(main_menu_keyboard_text[1])
    btn2 = types.KeyboardButton(main_menu_keyboard_text[2])
    btn3 = types.KeyboardButton(main_menu_keyboard_text[3])
    btn4 = types.KeyboardButton(main_menu_keyboard_text[4])
    keyboard.add(btn1, btn2)
    keyboard.add(btn3, btn4)
    return keyboard


# Функция для создания клавиатуры подменю 'Ближайшие'
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


def delete_transactions_keyboard(payment_uuid, reccurence_id):
    logging.info(f"pay: {payment_uuid}, recc: {reccurence_id}")
    markup = types.InlineKeyboardMarkup()
    message = None

    if reccurence_id:
        confirm_button = types.InlineKeyboardButton(
            "Одну",
            callback_data=f"confirm_delete_{payment_uuid}"
        )
        confirm_series_button = types.InlineKeyboardButton(
            "Серию",
            callback_data=f"series_delete_{reccurence_id}"
        )
        cancel_button = types.InlineKeyboardButton(
            "Отмена",
            callback_data="cancel_delete"
        )
        markup.add(confirm_button, confirm_series_button, cancel_button)
        message = "Удалить транзакции?"

    elif reccurence_id is None:
        confirm_button = types.InlineKeyboardButton(
            "Удалить",
            callback_data=f"confirm_delete_{payment_uuid}"
        )
        cancel_button = types.InlineKeyboardButton(
            "Отмена",
            callback_data="cancel_delete"
        )
        markup.add(confirm_button, cancel_button)
        message = "Удалить транзакцию?"

    return markup, message
