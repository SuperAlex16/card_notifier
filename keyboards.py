from telebot import types

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
