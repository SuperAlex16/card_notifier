# import telebot
# import asyncio
# from telebot import types
# from datetime import datetime, timedelta
# import openpyxl
# import sqlite3
# import schedule
# import time
# import threading
# import os
# from dotenv import load_dotenv
# import logging
# import uuid
# from calendar import monthrange
# from dateutil.relativedelta import relativedelta
#
#
# # Загрузка переменных окружения из файла .env
# load_dotenv()
#
# # Настройка логирования с поддержкой UTF-8
# logging.basicConfig(
#     level=logging.INFO,  # Уровень логирования
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('bot.log', encoding='utf-8'),  # Используем кодировку 'utf-8'
#         logging.StreamHandler()
#     ]
# )
#
# # Получение токена и chat_id из переменных окружения
# TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# chat_id = os.getenv('chat_id')
#
# if not TOKEN:
#     logging.error('Токен Telegram бота не установлен в файле .env.')
#     raise ValueError('TELEGRAM_BOT_TOKEN не установлен в файле .env.')
#
# if not chat_id:
#     logging.error('chat_id не установлен в файле .env.')
#     raise ValueError('chat_id не установлен в файле .env.')
#
# try:
#     chat_id = int(chat_id)  # Преобразование chat_id в целое число
# except ValueError:
#     logging.error('chat_id должен быть числом.')
#     raise ValueError('chat_id должен быть числом.')
#
# bot = telebot.TeleBot(TOKEN)
#
#
#
#
# # Словарь для хранения промежуточных данных о новой транзакции или редактируемом транзакцию
# payment_data = {}


# Функция для получения сокращенного дня недели на русском языке


# Функция для создания клавиатуры главного меню
# def main_menu_keyboard():
#     keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#     btn1 = types.KeyboardButton('📅 Что сегодня?')
#     btn2 = types.KeyboardButton('🔜 Ближайшие')
#     btn3 = types.KeyboardButton('➕ Добавить')
#     keyboard.add(btn1, btn2)
#     keyboard.add(btn3)
#     return keyboard
#
# # Функция для создания клавиатуры подменю 'Ближайшие'
# def nearest_menu_keyboard():
#     keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#     btn1 = types.KeyboardButton('3️⃣ дня')
#     btn2 = types.KeyboardButton('7️⃣ дней')
#     btn3 = types.KeyboardButton('3️⃣0️⃣ дней')
#     btn4 = types.KeyboardButton('🗓 Этот месяц')
#     back = types.KeyboardButton('◀️ Назад')
#     keyboard.add(btn1, btn2, btn3, btn4)
#     keyboard.add(back)
#     return keyboard


# Обработчик основного меню и подменю 'Ближайшие'


# Функция для получения транзакций по дате


# Функция для обновления статуса транзакции


# Функция для добавления транзакции


# Функция для отображения транзакций за сегодня
# def show_today(message):
#     current_date = datetime.now().date().isoformat()  # Форматируем в 'YYYY-MM-DD'
#     payments_today = get_transactions_by_date(current_date)
#
#     if payments_today:
#         for payment in payments_today:
#             weekday_short = get_weekday_short(datetime.strptime(payment['date'].split()[0], '%Y-%m-%d').date())
#             payment_str = f'{payment['date']} ({weekday_short}), {payment['card_name']}, {payment['transaction_type']} {payment['amount']:,.2f} руб.'
#             markup = types.InlineKeyboardMarkup()
#
#             # Кнопки для выполнения, редактирования и удаления
#             done_button = types.InlineKeyboardButton('✅', callback_data=f'done_{payment['uuid']}')
#             edit_button = types.InlineKeyboardButton('✏️', callback_data=f'edit_{payment['uuid']}')
#             delete_button = types.InlineKeyboardButton('🗑️', callback_data=f'delete_{payment['uuid']}')
#             markup.add(done_button, edit_button, delete_button)
#
#             bot.send_message(message.chat.id, payment_str, reply_markup=markup)
#         logging.info(f'Отправлены транзакции на сегодня пользователю {message.chat.id}.')
#     else:
#         bot.send_message(message.chat.id, 'Нет транзакций на сегодня.')
#         logging.info(f'Транзакций на сегодня нет. Информация отправлена пользователю {message.chat.id}.')


# Функция для отображения ближайших транзакций за заданное количество дней
# def show_nearest_days(message, days):
#     current_date = datetime.now().date()
#     date_limit = (current_date + timedelta(days=days)).isoformat()
#     payments = get_transactions_in_date_range(current_date.isoformat(), date_limit)
#
#     if payments:
#         for payment in payments:
#             weekday_short = get_weekday_short(datetime.strptime(payment['date'].split()[0], '%Y-%m-%d').date())
#             payment_str = f'{payment['date']} ({weekday_short}), {payment['card_name']}, {payment['transaction_type']} {payment['amount']:,.2f} руб.'
#             markup = types.InlineKeyboardMarkup()
#
#             # Кнопки для выполнения, редактирования и удаления
#             done_button = types.InlineKeyboardButton('✅', callback_data=f'done_{payment['uuid']}')
#             edit_button = types.InlineKeyboardButton('✏️', callback_data=f'edit_{payment['uuid']}')
#             delete_button = types.InlineKeyboardButton('🗑️', callback_data=f'delete_{payment['uuid']}')
#             markup.add(done_button, edit_button, delete_button)
#
#             bot.send_message(message.chat.id, payment_str, reply_markup=markup)
#         logging.info(f'Отправлены транзакции за следующие {days} дней пользователю {message.chat.id}.')
#     else:
#         bot.send_message(message.chat.id, f'Нет транзакций за следующие {days} дней.')
#         logging.info(f'Транзакций за следующие {days} дней нет. Информация отправлена пользователю {message.chat.id}.')


# Функция для отображения транзакций за текущий месяц
# def show_this_month(message):
#     current_date = datetime.now().date()
#     start_of_month = current_date.replace(day=1).isoformat()  # Первый день текущего месяца
#     end_of_month = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
#     end_of_month = end_of_month.isoformat()  # Последний день текущего месяца
#
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("""
#         SELECT * FROM transactions
#         WHERE date BETWEEN ? AND ? AND date >= ? AND execution_status = 0
#         ORDER BY date ASC, transaction_type = 'снять'
#     """, (start_of_month, end_of_month, current_date.isoformat()))
#     transactions = cursor.fetchall()
#     conn.close()
#
#     if transactions:
#         for payment in transactions:
#             weekday_short = get_weekday_short(datetime.strptime(payment['date'], '%Y-%m-%d').date())
#             payment_str = f'{payment['date']} ({weekday_short}), {payment['card_name']}, {payment['transaction_type']} {payment['amount']:,.2f} руб.'
#             markup = types.InlineKeyboardMarkup()
#
#             # Кнопки для выполнения, редактирования и удаления
#             done_button = types.InlineKeyboardButton('✅', callback_data=f'done_{payment['uuid']}')
#             edit_button = types.InlineKeyboardButton('✏️', callback_data=f'edit_{payment['uuid']}')
#             delete_button = types.InlineKeyboardButton('🗑️', callback_data=f'delete_{payment['uuid']}')
#             markup.add(done_button, edit_button, delete_button)
#
#             bot.send_message(message.chat.id, payment_str, reply_markup=markup)
#         logging.info(f'Отправлены предстоящие транзакции за текущий месяц пользователю {message.chat.id}.')
#     else:
#         bot.send_message(message.chat.id, 'Нет предстоящих транзакций на текущий месяц.')
#         logging.info(f'Предстоящих транзакций на текущий месяц нет. Информация отправлена пользователю {message.chat.id}.')


# Функция для начала процесса добавления новой транзакции
# def start_addition_process(message):
#     # Начало процесса добавления транзакции
#     ask_for_payment_details(message)
#     bot.register_next_step_handler(message, process_payment_data)

# Функция, которая выводит запрос на ввод данных о транзакции с кнопкой отмены
# def ask_for_payment_details(message):
#     markup = types.InlineKeyboardMarkup()
#     cancel_button = types.InlineKeyboardButton('❌ Отменить добавление', callback_data='cancel_addition')
#     markup.add(cancel_button)
#
#     bot.send_message(
#         message.chat.id,
#         'Введите дату (дд.мм.гггг), название карты, 'внести' или 'снять', сумму через пробел:',
#         reply_markup=markup
#     )


# Функция обработки введенных данных транзакции
# def process_payment_data(message):
#     try:
#         inputs = message.text.strip().split()
#         if len(inputs) != 4:
#             raise ValueError('Неверное количество параметров. Введите: дата карта тип сумма.')
#
#         date_str, card_name, transaction_type_input, amount_str = inputs
#         date = datetime.strptime(date_str, '%d.%m.%Y').date().isoformat()  # Преобразуем в формат 'YYYY-MM-DD'
#         transaction_type = transaction_type_input.lower()
#         amount = float(amount_str)
#
#         if transaction_type not in ['внести', 'снять']:
#             raise ValueError('Неверный тип транзакции. Используйте 'внести' или 'снять'.')
#
#         payment_uuid = str(uuid.uuid4())  # Генерация UUID для новой транзакции
#
#         # Проверка на редактирование: если операция редактирования
#         if message.chat.id in payment_data and 'edit_uuid' in payment_data[message.chat.id]:
#             old_uuid = payment_data[message.chat.id]['edit_uuid']
#
#             # Удаляем старую транзакцию из базы данных
#             delete_transaction(old_uuid, message.chat.id)
#             logging.info(f'Удалена старая транзакция с UUID {old_uuid} после редактирования.')
#
#             # Обновляем данные о редактируемой транзакции
#             payment_data[message.chat.id]['edit_uuid'] = payment_uuid  # Обновляем UUID на новый
#
#         # Добавление новой транзакции в базу данных
#         add_transaction(payment_uuid, date, card_name, transaction_type, amount)
#         logging.info(f'Добавлена новая транзакция с UUID {payment_uuid} для пользователя {message.chat.id}.')
#
#         # Сохраняем payment_uuid для последующей работы с повторением
#         if message.chat.id not in payment_data:
#             payment_data[message.chat.id] = {}
#         payment_data[message.chat.id]['last_payment_uuid'] = payment_uuid
#
#         # Спрашиваем пользователя о ежемесячном повторении
#         ask_for_monthly_recurrence(message)
#
#     except (ValueError, IndexError) as e:
#         bot.send_message(message.chat.id, 'Ошибка. Пожалуйста, проверьте формат ввода.')
#         logging.error(f'Ошибка при обработке данных транзакции: {e}')


# Функция для вопроса о повторении транзакции
# def ask_for_monthly_recurrence(message):
#     markup = types.InlineKeyboardMarkup()
#     yes_button = types.InlineKeyboardButton('Да', callback_data='recurrence_yes')
#     no_button = types.InlineKeyboardButton('Нет', callback_data='recurrence_no')
#     markup.add(yes_button, no_button)
#
#     bot.send_message(message.chat.id, 'Повторять ежемесячно?', reply_markup=markup)

# Обработчик выбора повторения транзакций


# Функция создания повторяющихся транзакций на 36 месяцев
import uuid  # Добавим, если не импортировано

import uuid

# def create_recurring_payments(payment_uuid, months):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     # Получаем исходную транзакцию и создаем уникальный recurrence_id для всей группы повторов
#     cursor.execute('SELECT date, card_name, transaction_type, amount FROM transactions WHERE uuid = ?', (payment_uuid,))
#     original_payment = cursor.fetchone()
#     recurrence_id = str(uuid.uuid4())  # Уникальный идентификатор для группы повторов
#
#     if original_payment:
#         initial_date = datetime.fromisoformat(original_payment['date']).date()
#         card_name = original_payment['card_name']
#         transaction_type = original_payment['transaction_type']
#         amount = original_payment['amount']
#
#         # Обновляем исходную транзакцию, устанавливая is_recursive и recurrence_id
#         cursor.execute("""
#             UPDATE transactions
#             SET recurrence_id = ?, is_recursive = 1
#             WHERE uuid = ?
#         """, (recurrence_id, payment_uuid))
#
#         # Создаем последующие транзакции с тем же recurrence_id и is_recursive = 1
#         for i in range(1, months + 1):
#             next_date = initial_date + relativedelta(months=i)
#             last_day_of_month = monthrange(next_date.year, next_date.month)[1]
#
#             if initial_date.day > last_day_of_month:
#                 next_date = next_date.replace(day=last_day_of_month)
#
#             new_payment_uuid = str(uuid.uuid4())
#             cursor.execute("""
#                 INSERT INTO transactions (uuid, date, card_name, transaction_type, amount, execution_status, recurrence_id, is_recursive)
#                 VALUES (?, ?, ?, ?, ?, 0, ?, 1)
#             """, (new_payment_uuid, next_date.isoformat(), card_name, transaction_type, amount, recurrence_id))
#
#         conn.commit()
#         logging.info(f'Созданы повторяющиеся транзакции для UUID {payment_uuid} на {months} месяцев с recurrence_id {recurrence_id}.')
#     else:
#         logging.error(f'Исходная транзакция с UUID {payment_uuid} не найдена.')
#
#     conn.close()


# Словарь для временного хранения удаленных транзакций
deleted_payments = {}


# Функция удаления платежа по UUID
def remove_payment_by_uuid(payment_uuid):
    rows = list(sheet.iter_rows(min_row=2, values_only=False))
    for row in rows:
        if row[0].value == payment_uuid:
            sheet.delete_rows(row[0].row, 1)
            logging.info(f"Платеж с UUID {payment_uuid} удален.")
            return
    logging.warning(f"Платеж с UUID {payment_uuid} не найден для удаления.")

# Функция редактирования платежей
def edit_payments(message):
    current_date = datetime.now().date()
    date_limit = current_date + timedelta(days=30)
    payments = []

# Функция редактирования транзакций
# def edit_payments(message):
#     current_date = datetime.now().date()
#     date_limit = current_date + timedelta(days=30)
#     payments = []
#
#     for row in sheet.iter_rows(min_row=2, values_only=True):
#         payment_uuid = row[0]
#         payment_date = row[1].date() if isinstance(row[1], datetime) else None
#         card_name = row[2]
#         transaction_type = row[3]
#         amount = row[4]
#         execution_status = row[5]
#
#         if payment_date and current_date <= payment_date <= date_limit and execution_status == 0:
#             weekday_short = get_weekday_short(payment_date)
#             payment_str = f'{payment_date.strftime('%d.%m.%Y')} ({weekday_short}), {card_name}, {transaction_type}, {amount:,.2f} руб.'
#             payments.append({'uuid': payment_uuid, 'description': payment_str, 'type': transaction_type})
#
#     if payments:
#         bot.send_message(message.chat.id, 'Транзакции за ближайшие 30 дней для редактирования:')
#         for payment in payments:
#             logging.info(f'Подготовка транзакции для редактирования с UUID: {payment['uuid']}')
#             markup = types.InlineKeyboardMarkup()
#             edit_button = types.InlineKeyboardButton('✏️ Редактировать', callback_data=f'edit_{payment['uuid']}')
#             markup.add(edit_button)
#             bot.send_message(message.chat.id, f'Транзакция: {payment['description']}', reply_markup=markup)
#         logging.info(f'Отправлены транзакции для редактирования пользователю {message.chat.id}.')
#     else:
#         bot.send_message(message.chat.id, 'Нет транзакций за ближайшие 30 дней для редактирования.')
#         logging.info(
#             f'Транзакций за ближайшие 30 дней для редактирования нет. Информация отправлена пользователю {message.chat.id}.')


    if payments:
        bot.send_message(message.chat.id, "Платежи за ближайшие 30 дней для редактирования:")
        for payment in payments:
            markup = types.InlineKeyboardMarkup()
            edit_button = types.InlineKeyboardButton("✏️ Редактировать", callback_data=f"edit_{payment['uuid']}")
            markup.add(edit_button)
            bot.send_message(message.chat.id, f"Платеж: {payment['description']}", reply_markup=markup)
        logging.info(f"Отправлены платежи для редактирования пользователю {message.chat.id}.")
    else:
        bot.send_message(message.chat.id, "Нет платежей за ближайшие 30 дней для редактирования.")
        logging.info(f"Платежей за ближайшие 30 дней для редактирования нет. Информация отправлена пользователю {message.chat.id}.")

# Обработчик callback-запросов (кнопок)


# def process_edit_payment(message):
#     try:
#         if message.chat.id not in payment_data or 'edit_uuid' not in payment_data[message.chat.id]:
#             bot.send_message(message.chat.id, 'Ошибка: транзакция для редактирования не найдена.')
#             return
#
#         payment_uuid = payment_data[message.chat.id]['edit_uuid']
#         conn = get_db_connection()
#         cursor = conn.cursor()
#
#         cursor.execute('SELECT recurrence_id, is_recursive FROM transactions WHERE uuid = ?', (payment_uuid,))
#         transaction = cursor.fetchone()
#         conn.close()
#
#         if transaction and transaction['is_recursive'] == 1:
#             recurrence_id = transaction['recurrence_id']
#             markup = types.InlineKeyboardMarkup()
#             edit_one_button = types.InlineKeyboardButton('Изменить только эту',
#                                                          callback_data=f'edit_one_{payment_uuid}')
#             edit_series_button = types.InlineKeyboardButton('Изменить всю серию',
#                                                             callback_data=f'edit_series_{recurrence_id}')
#             markup.add(edit_one_button, edit_series_button)
#
#             logging.info(f'Кнопки созданы: edit_one_{payment_uuid} и edit_series_{recurrence_id}')
#             bot.send_message(message.chat.id,
#                              'Эта транзакция является частью серии. Хотите изменить только её или всю серию?',
#                              reply_markup=markup)
#         else:
#             bot.send_message(message.chat.id, 'Введите новые данные в формате: дата карта тип сумма.')
#             bot.register_next_step_handler(message, edit_transaction_data, payment_uuid)
#
#     except Exception as e:
#         bot.send_message(message.chat.id, f'Ошибка: {str(e)}')
#         logging.error(f'Ошибка при редактировании транзакции: {str(e)}')


# def find_transaction(uuid):
#     original_uuid = uuid
#     if uuid.startswith('edit_one_'):
#         uuid = uuid.replace('edit_one_', '')
#     elif uuid.startswith('edit_series_'):
#         uuid = uuid.replace('edit_series_', '')
#
#     logging.info(f'Ищем транзакцию с UUID (исходный: {original_uuid}, без префикса: {uuid})')
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM transactions WHERE uuid = ?', (uuid,))
#     transaction = cursor.fetchone()
#     conn.close()
#
#     if transaction:
#         logging.info(f'Транзакция найдена: {transaction}')
#     else:
#         logging.warning(f'Транзакция с UUID {uuid} не найдена.')
#
#     return transaction


# def edit_transaction_data(message, payment_uuid):
#     logging.info(f'Функция edit_transaction_data вызвана для UUID: {payment_uuid}')
#     try:
#         # Получаем и разбираем введённые данные
#         inputs = message.text.strip().split()
#         if len(inputs) != 4:
#             bot.send_message(message.chat.id, 'Неверное количество параметров. Введите: дата карта тип сумма.')
#             return
#
#         date_str, card_name, transaction_type_input, amount_str = inputs
#         date = datetime.strptime(date_str, '%d.%m.%Y').date()
#         transaction_type = transaction_type_input.lower()
#         amount = float(amount_str)
#
#         if transaction_type not in ['внести', 'снять']:
#             bot.send_message(message.chat.id, 'Неверный тип транзакции. Используйте 'внести' или 'снять'.')
#             return
#
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("""
#             UPDATE transactions
#             SET date = ?, card_name = ?, transaction_type = ?, amount = ?
#             WHERE uuid = ?
#         """, (date, card_name, transaction_type, amount, payment_uuid))
#         conn.commit()
#         conn.close()
#
#         bot.send_message(message.chat.id, 'Транзакция успешно обновлена!')
#
#     except Exception as e:
#         bot.send_message(message.chat.id, f'Ошибка: {str(e)}')
#         logging.error(f'Ошибка при редактировании транзакции: {str(e)}')


# def edit_series_data(message, recurrence_id):
#     logging.info(f'Функция edit_series_data вызвана для recurrence_id: {recurrence_id}')
#     try:
#         inputs = message.text.strip().split()
#         if len(inputs) != 4:
#             bot.send_message(message.chat.id, 'Неверное количество параметров. Введите: дата карта тип сумма.')
#             return
#
#         date_str, card_name, transaction_type_input, amount_str = inputs
#         date = datetime.strptime(date_str, '%d.%m.%Y').date()
#         transaction_type = transaction_type_input.lower()
#         amount = float(amount_str)
#
#         if transaction_type not in ['внести', 'снять']:
#             bot.send_message(message.chat.id, 'Неверный тип транзакции. Используйте 'внести' или 'снять'.')
#             return
#
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("""
#             UPDATE transactions
#             SET date = ?, card_name = ?, transaction_type = ?, amount = ?
#             WHERE recurrence_id = ? AND date >= ?
#         """, (date, card_name, transaction_type, amount, recurrence_id, datetime.now().date().isoformat()))
#         conn.commit()
#         conn.close()
#
#         bot.send_message(message.chat.id, 'Все транзакции в серии успешно обновлены!')
#
#     except Exception as e:
#         bot.send_message(message.chat.id, f'Ошибка: {str(e)}')
#         logging.error(f'Ошибка при редактировании серии транзакций: {str(e)}')


# Функция для обновления статуса транзакции
# def update_transaction_status(uuid, status):
#     conn = sqlite3.connect('transactions.db')
#     cursor = conn.cursor()
#     cursor.execute("""
#         UPDATE transactions
#         SET execution_status = ?
#         WHERE UUID = ?
#     """, (status, uuid))
#
#     # Check if any rows were updated
#     if cursor.rowcount == 0:
#         logging.warning(f'Транзакция с UUID {uuid} не найдена для обновления.')
#     else:
#         logging.info(f'Транзакция с UUID {uuid} успешно обновлена.')
#
#     conn.commit()  # Save changes
#     conn.close()


# Функция для отправки напоминаний с кнопками 'Уже внес' или 'Уже снял'
# def send_reminder_with_buttons(payment_uuid, message_text, transaction_type):
#     """
#     Функция отправляет напоминание с кнопкой для обновления статуса транзакции.
#
#     Аргументы:
#     payment_uuid -- идентификатор транзакции (UUID).
#     message_text -- текст сообщения, который будет отправлен пользователю.
#     transaction_type -- тип транзакции ('внести' или 'снять').
#     """
#
#     # Создаем клавиатуру с кнопками
#     markup = types.InlineKeyboardMarkup()
#
#     # Добавляем соответствующую кнопку в зависимости от типа транзакции
#     if transaction_type.lower() == 'внести":
#         button = types.InlineKeyboardButton("☑️ Уже внес", callback_data=f"done_{payment_uuid}")
#     elif transaction_type.lower() == "снять":
#         button = types.InlineKeyboardButton("✅ Уже снял", callback_data=f"withdrawn_{payment_uuid}")
#     else:
#         # Если тип транзакции неизвестен, используем универсальную кнопку "Выполнено"
#         button = types.InlineKeyboardButton("✅ Выполнено", callback_data=f"done_{payment_uuid}")
#
#     markup.add(button)
#
#     # Логируем отправку напоминания для отладки
#     logging.info(f"Отправка напоминания: '{message_text}' с кнопкой для UUID {payment_uuid}")
#
#     # Пытаемся отправить сообщение с кнопкой
#     try:
#         bot.send_message(chat_id, message_text, reply_markup=markup)
#         logging.info("Напоминание успешно отправлено.")
#     except Exception as e:
#         logging.error(f"Ошибка при отправке напоминания: {e}")


# Запуск планировщика в отдельном потоке
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# Запланировать отправку напоминаний каждую минуту для теста
schedule.every(1).minutes.do(send_reminders)

# Запуск бота в отдельном потоке
bot_thread = threading.Thread(target=safe_polling, daemon=True)
bot_thread.start()

# Главный поток продолжает выполнение других задач, если нужно
while True:
    time.sleep(60)
