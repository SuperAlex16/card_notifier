import re

from telebot import types

from db_functions import init_db
from functions import (add_transaction, ask_for_amount, ask_for_monthly_recurrence, ask_for_transaction_date,
                       ask_for_card_name, ask_for_transaction_type, create_transactions_dict, create_uuid,
                       done_transactions, save_transactions_to_db, show_today, transaction_dict,
                       undo_save_transactions_to_db, undo_transactions, is_recurrence, delete_transactions,
                       start_addition_process, show_nearest_days, show_this_month, create_recurring_payments,
                       undo_delete_transactions)
from keyboards import (create_calendar, main_menu_keyboard, nearest_menu_keyboard, start_keyboard,
                       delete_transactions_keyboard, transactions_type_keyboard,
                       undo_save_transactions_to_db_keyboard)
from logger import logging
from remind_func import run_reminders
from settings import db_transaction_types, recurrent_count_months

user_states = {}


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

    @bot.callback_query_handler(func=lambda call: call.data.startswith('CALENDAR_'))
    def handle_calendar(call):
        chat_id = call.message.chat.id
        data = call.data.split('_')
        action = data[1]
        print(action)
        if action == "MONTH":
            year, month = int(data[2]), int(data[3])
            calendar = create_calendar(year, month)
            bot.edit_message_reply_markup(
                call.message.chat.id, call.message.message_id, reply_markup=calendar
            )

        elif action == "DAY":
            year, month, day = int(data[2]), int(data[3]), int(data[4])
            transaction_date = {
                "year": year,
                "month": month,
                "day": day
            }
            key = "date"
            create_transactions_dict(chat_id, key, transaction_date)
            bot.send_message(
                chat_id, f"Дата: {transaction_date['day']}/{transaction_date['month']}"
                         f"/{transaction_date['year']}"
            )
            ask_for_card_name(bot, chat_id)

    @bot.callback_query_handler(func=lambda call: call.data == "IGNORE")
    def ignore(call):
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("recurrence"))
    def handle_recurrence_selection(call):
        chat_id = call.message.chat.id
        recurrence_id = create_uuid()
        key = "recurrence_id"
        create_transactions_dict(chat_id, key, recurrence_id)

        date = str(transaction_dict[chat_id]['date']['day']) + '/' + str(
            transaction_dict[chat_id]['date']['month']
        ) + '/' + str(transaction_dict[chat_id]['date']['year'])

        transaction_type = transaction_dict[chat_id]['type']
        amount = transaction_dict[chat_id]['amount']
        card = transaction_dict[chat_id]['card']
        bot.send_message(
            chat_id, f"Добавлена повторяющаяся транзакция\n📅 {date}\n🔄 {transaction_type}\n💰 {amount}\n💳 {card}\n"

        )
        save_transactions_to_db(bot, chat_id, payment_uuid=None)
        markup = undo_save_transactions_to_db_keyboard(recurrence_id)
        bot.send_message(chat_id, "Отменить сохранение?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("no_recurrence"))
    def handle_recurrence_selection(call):
        chat_id = call.message.chat.id
        payment_uuid = create_uuid()
        recurrence_id = None
        key = "recurrence_id"
        create_transactions_dict(chat_id, key, recurrence_id)

        date = str(transaction_dict[chat_id]['date']['day']) + '/' + str(
            transaction_dict[chat_id]['date']['month']
        ) + '/' + str(transaction_dict[chat_id]['date']['year'])

        transaction_type = transaction_dict[chat_id]['type']
        amount = transaction_dict[chat_id]['amount']
        card = transaction_dict[chat_id]['card']

        bot.send_message(
            call.message.chat.id,
            f"Добавлена одиночная транзакция\n📅 {date}\n🔄 {transaction_type}\n💰 {amount}\n💳 {card}\n"
        )
        save_transactions_to_db(bot, chat_id, payment_uuid)
        markup = undo_save_transactions_to_db_keyboard(payment_uuid)
        bot.send_message(chat_id, "Отменить сохранение?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("undo_add_transactions_"))
    def handle_undo_add_transactions(call):
        chat_id = call.message.chat.id
        action_id = call.data.split('undo_add_transactions_')[1]

        undo_save_transactions_to_db(chat_id, action_id)

        bot.send_message(chat_id, "Транзакция не сохранена")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("select_card_"))
    def handle_card_selection(call):
        chat_id = call.message.chat.id
        card_name = call.data.split("select_card_")[1]
        bot.send_message(
            chat_id, f"Вы выбрали карту: {card_name}"
        )

        key = "card"
        create_transactions_dict(chat_id, key, card_name)
        ask_for_transaction_type(bot, chat_id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("add_new_card_"))
    def handle_new_card_creation(call):
        chat_id = call.message.chat.id

        bot.send_message(
            chat_id, f"Введите название карты:"
        )
        user_states[chat_id] = {
            "state": "waiting_for_card_name",
        }

    @bot.callback_query_handler(func=lambda call: call.data.startswith("deposit_"))
    def handle_deposit(call):
        chat_id = call.message.chat.id
        transaction_type = db_transaction_types[1]

        key = "type"
        create_transactions_dict(chat_id, key, transaction_type)

        bot.send_message(
            chat_id, f"Вы выбрали {transaction_type}"
        )
        ask_for_amount(bot, chat_id)
        user_states[chat_id] = {
            "state": "waiting_for_amount",
        }

    @bot.callback_query_handler(func=lambda call: call.data.startswith("withdraw_"))
    def handle_deposit(call):
        chat_id = call.message.chat.id
        transaction_type = db_transaction_types[2]

        key = "type"
        create_transactions_dict(chat_id, key, transaction_type)

        bot.send_message(
            chat_id, f"Вы выбрали {transaction_type}"
        )
        ask_for_amount(bot, chat_id)
        user_states[chat_id] = {
            "state": "waiting_for_amount",
        }

    @bot.message_handler(
        func=lambda message: user_states.get(message.chat.id, {}).get("state") == "waiting_for_card_name"
    )
    def handle_card_name_input(message):
        chat_id = message.chat.id
        card_name = message.text.strip()

        def is_valid_card_name(card_name):
            pattern = r'^[a-zA-Zа-яА-Я0-9 _-]+$'
            return bool(re.match(pattern, card_name))

        if not is_valid_card_name(card_name):
            bot.send_message(
                chat_id,
                "Недопустимое имя карты. Используйте только буквы, цифры, пробелы, дефисы или подчеркивания."
            )
            return

        user_states.pop(chat_id, None)

        bot.send_message(
            chat_id, f"Карта \"{card_name}\" сохранена. В следующий раз просто выбери ее из списка"
        )
        key = "card"
        create_transactions_dict(chat_id, key, card_name)
        ask_for_transaction_type(bot, chat_id)

    @bot.message_handler(
        func=lambda message: user_states.get(message.chat.id, {}).get("state") == "waiting_for_amount"
    )
    def handle_card_amount_input(message):
        chat_id = message.chat.id
        amount = message.text.strip()
        amount = re.sub(r"[^\d.]", ".", amount)

        if "." in amount:
            integer_part, decimal_part = amount.split(".", 1)
            decimal_part = decimal_part[:2]
            amount = f"{integer_part}.{decimal_part}"
        else:
            amount = amount

        if not re.fullmatch(r"^\d{1,6}(\.\d{1,2})?$", amount):
            bot.send_message(
                chat_id, "Пожалуйста, введите корректную сумму: до 6 цифр перед запятой"
            )
            return

        amount = float(amount)
        amount = f"{amount:.2f}"

        user_states.pop(chat_id, None)
        key = "amount"
        create_transactions_dict(chat_id, key, amount)

        bot.send_message(chat_id, f"Сумма: {amount}")

        ask_for_monthly_recurrence(bot, chat_id)

    @bot.message_handler(func=lambda message: True)
    def handle_menu(message):
        chat_id = message.chat.id
        if message.text == "📅 Что сегодня?":
            show_today(message, bot, chat_id)
        elif message.text == "🔜 Ближайшие":
            bot.send_message(message.chat.id, 'Выберите период:', reply_markup=nearest_menu_keyboard())
        elif message.text == "➕ Добавить":
            start_addition_process(bot, chat_id)
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

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback_query(call):
        logging.info(f'Received callback: {call.data} from user {call.from_user.id}')
        chat_id = call.message.chat.id
        # done
        if call.data.startswith('done_'):
            payment_uuid = call.data.replace('done_', '')
            done_transactions(chat_id, payment_uuid)

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
