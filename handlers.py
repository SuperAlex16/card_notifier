import re

from telebot import types

from db_functions import init_db
from functions import (done_transactions, show_today, undo_transactions, is_recurrence, delete_transactions,
                       start_addition_process, show_nearest_days, show_this_month, create_recurring_payments,
                       undo_delete_transactions)
from keyboards import main_menu_keyboard, nearest_menu_keyboard, start_keyboard, delete_transactions_keyboard
from remind_func import *
from settings import recurrent_count_months


def register_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == "/start")
    def handle_start_button(message):
        chat_id = message.chat.id
        logging.info(f"id пользователя: {chat_id}")
        init_db(chat_id)
        logging.info("Таблица в БД активирована")
        run_reminders(bot, chat_id)
        logging.info(f"Запущен run_reminders для чата {chat_id}")
        logging.info(f"Пользователь {chat_id} запустил бота")
        markup = start_keyboard()
        bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}", reply_markup=markup)

    @bot.message_handler(func=lambda message: True)
    def handle_menu(message):
        chat_id = message.chat.id
        if message.text == "📅 Что сегодня?":
            show_today(message, bot, chat_id)
        elif message.text == "🔜 Ближайшие":
            bot.send_message(message.chat.id, 'Выберите период:', reply_markup=nearest_menu_keyboard())
        elif message.text == "➕ Добавить":
            start_addition_process(message, bot, chat_id)
        # elif message.text == '✏️ Редактировать':
        #     edit_payments(message, bot)
        elif message.text == '3️⃣ дня':
            show_nearest_days(message, 3, bot)
        elif message.text == '7️⃣ дней':
            show_nearest_days(message, 7, bot)
        elif message.text == '3️⃣0️⃣ дней':
            show_nearest_days(message, 30, bot)
        elif message.text == '🗓 Этот месяц':
            show_this_month(message, bot, chat_id)
        elif message.text == '◀️ Назад':
            bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=main_menu_keyboard())
        else:
            bot.send_message(
                message.chat.id, 'Пожалуйста, выберите действие из меню:', reply_markup=main_menu_keyboard()
                )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("[recurrence"))
    def handle_recurrence_selection(call):
        match = re.match(r"\[(.*?)]_\[(.*?)]", call.data)
        action, payment_uuid = match.groups()
        print(f"action: {action}, UUID: {payment_uuid}")
        if action == 'recurrence_yes':
            create_recurring_payments(payment_uuid, recurrent_count_months, call.message.chat.id)
            bot.send_message(
                call.message.chat.id,
                f"Транзакция будет повторяться ежемесячно в течение {recurrent_count_months} месяцев."
                )
        elif action == 'recurrence_no':
            bot.send_message(call.message.chat.id, 'Транзакция добавлена без повторения.')
        else:
            bot.send_message(call.message.chat.id, 'Ошибка: данные транзакции не найдены.')

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback_query(call):
        logging.info(f'Received callback: {call.data} from user {call.from_user.id}')
        chat_id = call.message.chat.id
        # done
        if call.data.startswith('done_'):
            payment_uuid = call.data.replace('done_', '')
            done_transactions(chat_id, bot, payment_uuid)

            markup = types.InlineKeyboardMarkup()
            undo_button = types.InlineKeyboardButton('❌ Отменить', callback_data=f'undo_done_{payment_uuid}')
            markup.add(undo_button)

            bot.send_message(
                call.message.chat.id,
                "Транзакция выполнена. Вы можете отменить действие:",
                reply_markup=markup
                )

        elif call.data.startswith('undo_done_'):
            payment_uuid = call.data.replace('undo_done_', '')
            undo_transactions(chat_id, payment_uuid)

            bot.send_message(call.message.chat.id, "Выполнение отменено. Транзакция восстановлена.")

        elif call.data.startswith("delete_"):
            payment_uuid = call.data.replace("delete_", "")
            recurrence_id = is_recurrence(chat_id, payment_uuid)
            markup, message = delete_transactions_keyboard(payment_uuid, recurrence_id)

            bot.send_message(call.message.chat.id, f"{message}", reply_markup=markup)

        elif call.data.startswith("confirm_delete_"):
            payment_uuid = call.data.replace("confirm_delete_", "")

            delete_transactions(call.message.chat.id, payment_id=payment_uuid, recurrence_id=None)

            markup = types.InlineKeyboardMarkup()
            undo_button = types.InlineKeyboardButton(
                "❌ Отменить", callback_data=f"undo_delete_{payment_uuid}"
                )
            markup.add(undo_button)

            bot.send_message(
                call.message.chat.id, "Транзакция удалена. Вы можете отменить удаление:", reply_markup=markup
                )

        elif call.data.startswith("series_delete_"):
            recurrence_id = call.data.replace("series_delete_", "")

            delete_transactions(chat_id, payment_id=None, recurrence_id=recurrence_id)

            markup = types.InlineKeyboardMarkup()
            undo_button = types.InlineKeyboardButton(
                "❌ Отменить", callback_data=f"undo_series_delete_{recurrence_id}"
                )
            markup.add(undo_button)

            bot.send_message(
                call.message.chat.id,
                "Серия транзакций удалена. Вы можете отменить удаление:",
                reply_markup=markup
                )

        elif call.data.startswith("undo_delete_"):
            payment_uuid = call.data.replace("undo_delete_", "")

            undo_delete_transactions(chat_id, payment_id=payment_uuid, recurrence_id=None)

            bot.send_message(call.message.chat.id, "Удаление отменено. Транзакция восстановлена.")

        elif call.data.startswith("undo_series_delete_"):
            recurrence_id = call.data.replace("undo_series_delete_", "")

            undo_delete_transactions(chat_id, payment_id=None, recurrence_id=recurrence_id)

            bot.send_message(call.message.chat.id, "Удаление отменено. Серия транзакций восстановлена.")
