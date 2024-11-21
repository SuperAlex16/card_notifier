import re

from db_functions import init_db
from remind_func import *
from functions import *
from keyboards import main_menu_keyboard, nearest_menu_keyboard, start_keyboard, delete_transactions_keyboard
from logger import logging
from settings import reccurent_count_months


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
        elif message.text == '✏️ Редактировать':
            edit_payments(message, bot)
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
            bot.send_message(message.chat.id,
                'Пожалуйста, выберите действие из меню:',
                reply_markup=main_menu_keyboard())

    @bot.callback_query_handler(func=lambda call: call.data.startswith("[recurrence"))
    def handle_recurrence_selection(call):
        match = re.match(r"\[(.*?)\]_\[(.*?)\]", call.data)
        action, payment_uuid = match.groups()
        print(f"action: {action}, UUID: {payment_uuid}")
        if action == 'recurrence_yes':
            create_recurring_payments(payment_uuid, reccurent_count_months, call.message.chat.id)
            bot.send_message(call.message.chat.id,
                f"Транзакция будет повторяться ежемесячно в течение {reccurent_count_months} месяцев.")
        elif action == 'recurrence_no':
            bot.send_message(call.message.chat.id, 'Транзакция добавлена без повторения.')
        else:
            bot.send_message(call.message.chat.id, 'Ошибка: данные транзакции не найдены.')

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback_query(call):
        logging.info(f'Received callback: {call.data} from user {call.from_user.id}')
        chat_id = call.message.chat.id

        if call.data.startswith('done_') or call.data.startswith('withdrawn_'):
            payment_uuid = call.data.split('_')[1]
            new_status = 1 if call.data.startswith('done_') else 0
            update_transaction_status(payment_uuid, new_status, chat_id)

            # Добавляем кнопку 'Готово. Отменить?' для возможности отмены выполнения
            markup = types.InlineKeyboardMarkup()
            undo_button = types.InlineKeyboardButton('❌ Готово. Отменить?',
                callback_data=f'undo_done_{payment_uuid}_reminder')
            markup.add(undo_button)

            try:
                bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup)
                bot.answer_callback_query(call.id, 'Статус транзакции обновлён.')
            except Exception as e:
                logging.error(f'Ошибка при редактировании сообщения: {e}')
                bot.answer_callback_query(call.id, 'Не удалось обновить статус транзакции.')

        elif call.data.startswith('undo_done_'):
            # Проверяем, был ли это отмененный статус для напоминания или обычной транзакции
            data_parts = call.data.split('_')
            payment_uuid = data_parts[2]
            is_reminder = data_parts[-1] == 'reminder'

            # Получаем транзакцию для определения типа кнопок
            transaction = get_transaction_by_uuid(payment_uuid, chat_id)
            if transaction:
                markup = types.InlineKeyboardMarkup()

                # Если это отмена выполнения для напоминания, возвращаем одну кнопку
                if is_reminder:
                    if transaction['transaction_type'].lower() == 'внести':
                        original_button = types.InlineKeyboardButton('☑️ Уже внес',
                            callback_data=f'done_{payment_uuid}')
                    elif transaction['transaction_type'].lower() == 'снять':
                        original_button = types.InlineKeyboardButton('✅ Уже снял',
                            callback_data=f'withdrawn_{payment_uuid}')
                    else:
                        original_button = types.InlineKeyboardButton('✅ Выполнено',
                            callback_data=f'done_{payment_uuid}')
                    markup.add(original_button)
                else:
                    # Если это отмена выполнения для обычной транзакции, возвращаем три кнопки
                    done_button = types.InlineKeyboardButton('✅', callback_data=f'done_{payment_uuid}')
                    edit_button = types.InlineKeyboardButton('✏️', callback_data=f'edit_{payment_uuid}')
                    delete_button = types.InlineKeyboardButton('🗑️', callback_data=f'delete_{payment_uuid}')
                    markup.add(done_button, edit_button, delete_button)

                try:
                    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=markup)
                    bot.answer_callback_query(call.id, 'Отмена выполнена.')
                except Exception as e:
                    logging.error(f'Ошибка при редактировании сообщения: {e}')
                    bot.answer_callback_query(call.id, 'Не удалось отменить выполнение транзакции.')

        elif call.data.startswith('undo_done_'):
            # Извлекаем UUID для отмены
            payment_uuid = call.data.replace('undo_done_', '')
            update_transaction_status(payment_uuid, chat_id, 0)
            logging.info(f'Транзакция с UUID {payment_uuid} отменена.')

            # Восстановление начальных кнопок: выполнить или внести/снять
            markup = types.InlineKeyboardMarkup()
            done_button = types.InlineKeyboardButton('✅', callback_data=f'done_{payment_uuid}')
            withdrawn_button = types.InlineKeyboardButton('✅ Уже снял',
                callback_data=f'withdrawn_{payment_uuid}')
            markup.add(done_button, withdrawn_button)

            try:
                # Обновляем сообщение с кнопками
                bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup)
                bot.answer_callback_query(call.id, "Отметка отменена.")
            except Exception as e:
                logging.error(f"Ошибка при редактировании сообщения: {e}")
                bot.answer_callback_query(call.id, "Не удалось отменить отметку транзакции.")

            # Обновление статуса транзакции на 0 (не выполнено)
            update_transaction_status(payment_uuid, chat_id, 0)
            logging.info(f"Транзакция с UUID {payment_uuid} отменена.")

            # Восстановление всех кнопок: выполнение, редактирование, удаление
            markup = types.InlineKeyboardMarkup()
            done_button = types.InlineKeyboardButton("✅", callback_data=f"done_{payment_uuid}")
            edit_button = types.InlineKeyboardButton("✏️", callback_data=f"edit_{payment_uuid}")
            delete_button = types.InlineKeyboardButton("🗑️", callback_data=f"delete_{payment_uuid}")
            markup.add(done_button, edit_button, delete_button)

            try:
                # Обновляем сообщение с кнопками
                bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup)
                bot.answer_callback_query(call.id, "Отметка отменена.")
            except Exception as e:
                logging.error(f"Ошибка при редактировании сообщения: {e}")
                bot.answer_callback_query(call.id, "Не удалось отменить отметку транзакции.")

        elif call.data.startswith("delete_"):
            payment_uuid = call.data.replace("delete_", "")
            recurrence_id = is_recurrence(chat_id, payment_uuid)
            markup, message = delete_transactions_keyboard(payment_uuid, recurrence_id)

            bot.send_message(call.message.chat.id, f"{message}", reply_markup=markup)


        # Удаление транзакции с возможностью отмены
        elif call.data.startswith("confirm_delete_"):
            payment_uuid = call.data.replace("confirm_delete_", "")

            delete_transactions(call.message.chat.id, bot, payment_id=payment_uuid, reccurence_id=None)

            markup = types.InlineKeyboardMarkup()
            undo_button = types.InlineKeyboardButton("❌ Отменить удаление",
                callback_data=f"undo_delete_{payment_uuid}")
            markup.add(undo_button)

            bot.send_message(call.message.chat.id,
                "Транзакция удалена. Вы можете отменить удаление:",
                reply_markup=markup)

        elif call.data.startswith("series_delete_"):
            reccurence_id = call.data.replace("series_delete_", "")

            delete_transactions(call.message.chat.id, bot, payment_id=None, reccurence_id=reccurence_id)

            markup = types.InlineKeyboardMarkup()
            undo_button = types.InlineKeyboardButton("❌ Отменить удаление серии",
                callback_data=f"undo_series_delete_{reccurence_id}")
            markup.add(undo_button)

            bot.send_message(call.message.chat.id,
                "Серия транзакций удалена. Вы можете отменить удаление:",
                reply_markup=markup)

        elif call.data.startswith("undo_delete_"):
            payment_uuid = call.data.replace("undo_delete_", "")

            undo_delete_transactions(call.message.chat.id, bot, payment_id=payment_uuid, reccurence_id=None)

            bot.send_message(call.message.chat.id,
                    "Удаление отменено. Транзакция восстановлена.")

        elif call.data.startswith("undo_series_delete_"):
            reccurence_id = call.data.replace("undo_series_delete_", "")

            undo_delete_transactions(call.message.chat.id, bot, payment_id=None, reccurence_id=reccurence_id)

            bot.send_message(call.message.chat.id,
                    "Удаление отменено. Серия транзакций восстановлена.")