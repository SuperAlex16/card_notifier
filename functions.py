import logging
import sqlite3
import time
import uuid
from calendar import monthrange
from datetime import datetime, timedelta

import schedule
import telebot
from dateutil.relativedelta import relativedelta
from telebot import types

from db_functions import get_db_connection
# from bot import chat_id
from logger import logging
from settings import reminder_today_times, reminder_tomorrow_time


# Функция для отображения платежей на сегодня
def show_today(message, bot, chat_id):
    current_date = datetime.now().date().isoformat()  # Форматируем в 'YYYY-MM-DD'
    payments_today = get_transactions_by_date(current_date, chat_id)

    if payments_today:
        for payment in payments_today:
            weekday_short = get_weekday_short(datetime.strptime(payment['date'].split()[0], '%Y-%m-%d').date())
            payment_str = f'{payment['date']} ({weekday_short}), {payment['card_name']}, {payment['transaction_type']} {payment['amount']:,.2f} руб.'
            markup = types.InlineKeyboardMarkup()

            # Кнопки для выполнения, редактирования и удаления
            done_button = types.InlineKeyboardButton('✅', callback_data=f'done_{payment['uuid']}')
            edit_button = types.InlineKeyboardButton('✏️', callback_data=f'edit_{payment['uuid']}')
            delete_button = types.InlineKeyboardButton('🗑️', callback_data=f'delete_{payment['uuid']}')
            markup.add(done_button, edit_button, delete_button)

            bot.send_message(message.chat.id, payment_str, reply_markup=markup)
        logging.info(f'Отправлены транзакции на сегодня пользователю {message.chat.id}.')
    else:
        bot.send_message(message.chat.id, 'Нет транзакций на сегодня.')
        logging.info(f'Транзакций на сегодня нет. Информация отправлена пользователю {message.chat.id}.')


def add_payment(message, bot):
    bot.send_message(message.chat.id, 'Введите данные нового платежа (например, дата, сумма и тип):')
    # Здесь можно добавить код для обработки ввода и сохранения нового платежа в Excel


def edit_payments(message, bot):
    ### TODO исправить логику для работы с БД.
    current_date = datetime.now().date()
    date_limit = current_date + timedelta(days=30)
    payments = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        payment_uuid = row[0]
        payment_date = row[1].date() if isinstance(row[1], datetime) else None
        card_name = row[2]
        transaction_type = row[3]
        amount = row[4]
        execution_status = row[5]

        if payment_date and current_date <= payment_date <= date_limit and execution_status == 0:
            weekday_short = get_weekday_short(payment_date)
            payment_str = f'{payment_date.strftime('%d.%m.%Y')} ({weekday_short}), {card_name}, {transaction_type}, {amount:,.2f} руб.'
            payments.append({'uuid': payment_uuid, 'description': payment_str, 'type': transaction_type})

    if payments:
        bot.send_message(message.chat.id, 'Транзакции за ближайшие 30 дней для редактирования:')
        for payment in payments:
            logging.info(f'Подготовка транзакции для редактирования с UUID: {payment['uuid']}')
            markup = types.InlineKeyboardMarkup()
            edit_button = types.InlineKeyboardButton('✏️ Редактировать', callback_data=f'edit_{payment['uuid']}')
            markup.add(edit_button)
            bot.send_message(message.chat.id, f'Транзакция: {payment['description']}', reply_markup=markup)
        logging.info(f'Отправлены транзакции для редактирования пользователю {message.chat.id}.')
    else:
        bot.send_message(message.chat.id, 'Нет транзакций за ближайшие 30 дней для редактирования.')
        logging.info(
            f'Транзакций за ближайшие 30 дней для редактирования нет. Информация отправлена пользователю {message.chat.id}.')


def show_nearest_days(message, days, bot):
    current_date = datetime.now().date()
    date_limit = (current_date + timedelta(days=days)).isoformat()
    payments = get_transactions_in_date_range(current_date.isoformat(), date_limit)

    if payments:
        for payment in payments:
            weekday_short = get_weekday_short(datetime.strptime(payment['date'].split()[0], '%Y-%m-%d').date())
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
        bot.send_message(message.chat.id, f'Нет транзакций за следующие {days} дней.')
        logging.info(f'Транзакций за следующие {days} дней нет. Информация отправлена пользователю {message.chat.id}.')


def show_this_month(message, bot, chat_id):
    current_date = datetime.now().date()
    start_of_month = current_date.replace(day=1).isoformat()  # Первый день текущего месяца
    end_of_month = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    end_of_month = end_of_month.isoformat()  # Последний день текущего месяца

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
            SELECT * FROM '{chat_id}'
            WHERE date BETWEEN ? AND ? AND date >= ? AND execution_status = 0
            ORDER BY date ASC, transaction_type = 'снять'
        """, (start_of_month, end_of_month, current_date.isoformat()))
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
        bot.send_message(message.chat.id, 'Нет предстоящих транзакций на текущий месяц.')
        logging.info(
            f'Предстоящих транзакций на текущий месяц нет. Информация отправлена пользователю {message.chat.id}.')


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


def start_addition_process(message, bot):
    # Начало процесса добавления транзакции
    ask_for_payment_details(message, bot)
    bot.register_next_step_handler(message, process_payment_data)


def ask_for_payment_details(message, bot):
    markup = types.InlineKeyboardMarkup()
    cancel_button = types.InlineKeyboardButton('❌ Отменить добавление', callback_data='cancel_addition')
    markup.add(cancel_button)

    bot.send_message(
        message.chat.id,
        'Введите дату (дд.мм.гггг), название карты, внести или снять, сумму (через пробел):',
        reply_markup=markup
    )


def get_transactions_by_date(date, chat_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
                SELECT * FROM "{chat_id}"
                WHERE date = ? AND execution_status = 0
                ORDER BY date ASC, transaction_type = 'снять'  -- Сначала 'внести', затем 'снять'
                """, (date,))
    transactions = cursor.fetchall()
    conn.close()
    return transactions


def process_payment_data(message):
    try:
        inputs = message.text.strip().split()
        if len(inputs) != 4:
            raise ValueError('Неверное количество параметров. Введите: дата карта тип сумма.')

        date_str, card_name, transaction_type_input, amount_str = inputs
        date = datetime.strptime(date_str, '%d.%m.%Y').date().isoformat()  # Преобразуем в формат 'YYYY-MM-DD'
        transaction_type = transaction_type_input.lower()
        amount = float(amount_str)

        if transaction_type not in ['внести', 'снять']:
            raise ValueError("Неверный тип транзакции. Используйте ВНЕСТИ или СНЯТЬ")

            payment_uuid = str(uuid.uuid4())  # Генерация UUID для новой транзакции

            # Проверка на редактирование: если операция редактирования
            if message.chat.id in payment_data and 'edit_uuid' in payment_data[message.chat.id]:
                old_uuid = payment_data[message.chat.id]['edit_uuid']

                # Удаляем старую транзакцию из базы данных
                delete_transaction(old_uuid, message.chat.id)
                logging.info(f'Удалена старая транзакция с UUID {old_uuid} после редактирования.')

                # Обновляем данные о редактируемой транзакции
                payment_data[message.chat.id]['edit_uuid'] = payment_uuid  # Обновляем UUID на новый

            # Добавление новой транзакции в базу данных
            add_transaction(payment_uuid, date, card_name, transaction_type, amount)
            logging.info(f'Добавлена новая транзакция с UUID {payment_uuid} для пользователя {message.chat.id}.')

            # Сохраняем payment_uuid для последующей работы с повторением
            if message.chat.id not in payment_data:
                payment_data[message.chat.id] = {}
            payment_data[message.chat.id]['last_payment_uuid'] = payment_uuid

            # Спрашиваем пользователя о ежемесячном повторении
            ask_for_monthly_recurrence(message)

    except (ValueError, IndexError) as e:
        bot.send_message(message.chat.id, 'Ошибка. Пожалуйста, проверьте формат ввода.')
        logging.error(f'Ошибка при обработке данных транзакции: {e}')


def add_transaction(uuid, date, card_name, transaction_type, amount, execution_status=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (uuid, date, card_name, transaction_type, amount, execution_status)
        VALUES (?, ?, ?, ?, ?, ?)
                """, (uuid, date, card_name, transaction_type, amount, execution_status))
    conn.commit()
    conn.close()


def delete_transaction(uuid, chat_id, bot):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Проверяем, является ли транзакция рекурсивной
    cursor.execute('SELECT recurrence_id, is_recursive FROM transactions WHERE uuid = ?', (uuid,))
    transaction = cursor.fetchone()
    conn.close()

    if transaction and transaction['is_recursive'] == 1:
        recurrence_id = transaction['recurrence_id']

        # Создаём кнопки для выбора удаления одной транзакции или всей серии
        markup = types.InlineKeyboardMarkup()
        delete_one_button = types.InlineKeyboardButton('Удалить только эту', callback_data=f"delete_one_{uuid}")
        delete_series_button = types.InlineKeyboardButton("Удалить всю серию",
                                                          callback_data=f"delete_series_{recurrence_id}")
        markup.add(delete_one_button, delete_series_button)

        # Используем chat_id, переданный в функцию
        bot.send_message(chat_id, "Эта транзакция является частью серии. Хотите удалить только её или всю серию?",
                         reply_markup=markup)
    else:
        delete_one_transaction(uuid)  # Удаляем только одну транзакцию, если она не рекурсивная


def ask_for_monthly_recurrence(message, bot):
    markup = types.InlineKeyboardMarkup()
    yes_button = types.InlineKeyboardButton("Да", callback_data="recurrence_yes")
    no_button = types.InlineKeyboardButton("Нет", callback_data="recurrence_no")
    markup.add(yes_button, no_button)

    bot.send_message(message.chat.id, "Повторять ежемесячно?", reply_markup=markup)


def update_transaction_status(uuid, status):
    """
    Функция обновляет статус выполнения транзакции в таблице transactions.

    Аргументы:
    uuid -- идентификатор транзакции, которая должна быть обновлена.
    status -- новый статус (1 для выполнено, 0 для не выполнено).
    """

    # Подключаемся к базе данных SQLite
    conn = sqlite3.connect('transactions.db')
    cursor = conn.cursor()

    # Логируем параметры перед обновлением
    logging.info(f"Попытка обновить статус транзакции UUID {uuid} на статус {status}")

    # Выполняем обновление статуса транзакции
    cursor.execute("""
                UPDATE transactions
                SET execution_status = ?
                WHERE UUID = ?
                """, (status, uuid))

    # Проверяем, была ли обновлена хотя бы одна строка
    if cursor.rowcount == 0:
        logging.warning(f"Транзакция с UUID {uuid} не найдена для обновления статуса.")
    else:
        logging.info(f"Статус транзакции с UUID {uuid} успешно обновлён на {status}.")

    # Сохраняем изменения и закрываем подключение
    conn.commit()
    conn.close()
    logging.info(f"Проверка после commit: UUID {uuid}, новый статус: {status}")


def delete_one_transaction(uuid):
    logging.info(f"Функция delete_one_transaction вызвана для UUID: {uuid}")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
                INSERT INTO deleted_transactions (uuid, date, card_name, transaction_type, amount, execution_status, recurrence_id, is_recursive)
                SELECT uuid, date, card_name, transaction_type, amount, execution_status, recurrence_id, is_recursive
                FROM transactions
                WHERE uuid = ?
                """, (uuid,))

    cursor.execute('DELETE FROM transactions WHERE uuid = ?', (uuid,))
    conn.commit()
    logging.info(f"Только транзакция с UUID {uuid} удалена.")
    conn.close()


def delete_series(recurrence_id):
    logging.info(f"Функция delete_series вызвана для recurrence_id: {recurrence_id}")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
                INSERT INTO deleted_transactions (uuid, date, card_name, transaction_type, amount, execution_status, recurrence_id, is_recursive)
                SELECT uuid, date, card_name, transaction_type, amount, execution_status, recurrence_id, is_recursive
                FROM transactions
                WHERE recurrence_id = ?
                """, (recurrence_id,))

    cursor.execute('DELETE FROM transactions WHERE recurrence_id = ?', (recurrence_id,))
    conn.commit()
    logging.info(f"Все транзакции с recurrence_id {recurrence_id} удалены.")
    conn.close()


def restore_transaction(uuid=None, recurrence_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if recurrence_id:
        # Логируем количество транзакций, которые будут восстановлены
        cursor.execute('SELECT COUNT(*) FROM deleted_transactions WHERE recurrence_id = ?', (recurrence_id,))
        count = cursor.fetchone()[0]
        logging.info(f"Найдено для восстановления по recurrence_id {recurrence_id}: {count} транзакций")

        # Восстанавливаем всю серию по recurrence_id
        cursor.execute("""
                INSERT INTO transactions (uuid, date, card_name, transaction_type, amount, execution_status, recurrence_id, is_recursive)
                SELECT uuid, date, card_name, transaction_type, amount, execution_status, recurrence_id, is_recursive
                FROM deleted_transactions
                WHERE recurrence_id = ?
                """, (recurrence_id,))

        # Удаляем восстановленные транзакции из deleted_transactions
        cursor.execute('DELETE FROM deleted_transactions WHERE recurrence_id = ?', (recurrence_id,))
        logging.info(f"Восстановлены все транзакции с recurrence_id {recurrence_id}.")

    elif uuid:
        # Восстанавливаем только одну транзакцию по её UUID
        cursor.execute("""
                INSERT INTO transactions (uuid, date, card_name, transaction_type, amount, execution_status, recurrence_id, is_recursive)
                SELECT uuid, date, card_name, transaction_type, amount, execution_status, recurrence_id, is_recursive
                FROM deleted_transactions
                WHERE uuid = ?
                """, (uuid,))

        cursor.execute('DELETE FROM deleted_transactions WHERE uuid = ?', (uuid,))
        logging.info(f"Восстановлена транзакция с UUID {uuid}.")

    conn.commit()
    conn.close()


def get_transactions_in_date_range(start_date, end_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                SELECT * FROM transactions
                WHERE date BETWEEN ? AND ? AND execution_status = 0
                ORDER BY date ASC, transaction_type = 'снять'
                """, (start_date, end_date))
    transactions = cursor.fetchall()
    conn.close()
    return transactions


def create_recurring_payments(payment_uuid, months):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем исходную транзакцию и создаем уникальный recurrence_id для всей группы повторов
    cursor.execute("SELECT date, card_name, transaction_type, amount FROM transactions WHERE uuid = ?",
                   (payment_uuid,))
    original_payment = cursor.fetchone()
    recurrence_id = str(uuid.uuid4())  # Уникальный идентификатор для группы повторов

    if original_payment:
        initial_date = datetime.fromisoformat(original_payment['date']).date()
        card_name = original_payment['card_name']
        transaction_type = original_payment['transaction_type']
        amount = original_payment['amount']

        # Обновляем исходную транзакцию, устанавливая is_recursive и recurrence_id
        cursor.execute("""
                UPDATE transactions
                SET recurrence_id = ?, is_recursive = 1
                WHERE uuid = ?
                """, (recurrence_id, payment_uuid))

        # Создаем последующие транзакции с тем же recurrence_id и is_recursive = 1
        for i in range(1, months + 1):
            next_date = initial_date + relativedelta(months=i)
            last_day_of_month = monthrange(next_date.year, next_date.month)[1]

            if initial_date.day > last_day_of_month:
                next_date = next_date.replace(day=last_day_of_month)

            new_payment_uuid = str(uuid.uuid4())
            cursor.execute("""
        INSERT INTO transactions (uuid, date, card_name, transaction_type, amount, execution_status, recurrence_id, is_recursive)
        VALUES (?, ?, ?, ?, ?, 0, ?, 1)
    """, (new_payment_uuid, next_date.isoformat(), card_name, transaction_type, amount, recurrence_id))

        conn.commit()
        logging.info(
            f"Созданы повторяющиеся транзакции для UUID {payment_uuid} на {months} месяцев с recurrence_id {recurrence_id}.")
    else:
        logging.error(f"Исходная транзакция с UUID {payment_uuid} не найдена.")

    conn.close()


def update_payment_status(payment_uuid, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                UPDATE transactions
                SET execution_status = ?
                WHERE uuid = ?
                """, (status, payment_uuid))

    if cursor.rowcount > 0:
        conn.commit()
        logging.info(f"Статус транзакции с UUID {payment_uuid} обновлён на {status}.")
    else:
        logging.warning(f"Транзакция с UUID {payment_uuid} не найдена для обновления статуса.")

    conn.close()


def get_transaction_by_uuid(uuid):
    logging.info(f"Ищем транзакцию с UUID: {uuid}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions WHERE uuid = ?', (uuid,))
    transaction = cursor.fetchone()
    if transaction is None:
        logging.warning(f"Транзакция с UUID {uuid} не найдена.")
    conn.close()
    logging.info(f"Результат поиска: {transaction}")
    return transaction


def process_edit_payment(message, bot):
    try:
        if message.chat.id not in payment_data or 'edit_uuid' not in payment_data[message.chat.id]:
            bot.send_message(message.chat.id, "Ошибка: транзакция для редактирования не найдена.")
            return

        payment_uuid = payment_data[message.chat.id]['edit_uuid']
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT recurrence_id, is_recursive FROM transactions WHERE uuid = ?", (payment_uuid,))
        transaction = cursor.fetchone()
        conn.close()

        if transaction and transaction['is_recursive'] == 1:
            recurrence_id = transaction['recurrence_id']
            markup = types.InlineKeyboardMarkup()
            edit_one_button = types.InlineKeyboardButton("Изменить только эту",
                                                         callback_data=f"edit_one_{payment_uuid}")
            edit_series_button = types.InlineKeyboardButton("Изменить всю серию",
                                                            callback_data=f"edit_series_{recurrence_id}")
            markup.add(edit_one_button, edit_series_button)

            logging.info(f"Кнопки созданы: edit_one_{payment_uuid} и edit_series_{recurrence_id}")
            bot.send_message(message.chat.id,
                             "Эта транзакция является частью серии. Хотите изменить только её или всю серию?",
                             reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Введите новые данные в формате: дата карта тип сумма.")
            bot.register_next_step_handler(message, edit_transaction_data, payment_uuid)

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
        logging.error(f"Ошибка при редактировании транзакции: {str(e)}")


def find_transaction(uuid):
    original_uuid = uuid
    if uuid.startswith("edit_one_"):
        uuid = uuid.replace("edit_one_", "")
    elif uuid.startswith("edit_series_"):
        uuid = uuid.replace("edit_series_", "")

    logging.info(f"Ищем транзакцию с UUID (исходный: {original_uuid}, без префикса: {uuid})")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE uuid = ?", (uuid,))
    transaction = cursor.fetchone()
    conn.close()

    if transaction:
        logging.info(f"Транзакция найдена: {transaction}")
    else:
        logging.warning(f"Транзакция с UUID {uuid} не найдена.")

    return transaction


def edit_transaction_data(message, payment_uuid, bot):
    logging.info(f"Функция edit_transaction_data вызвана для UUID: {payment_uuid}")
    try:
        # Получаем и разбираем введённые данные
        inputs = message.text.strip().split()
        if len(inputs) != 4:
            bot.send_message(message.chat.id, "Неверное количество параметров. Введите: дата карта тип сумма.")
            return

        date_str, card_name, transaction_type_input, amount_str = inputs
        date = datetime.strptime(date_str, "%d.%m.%Y").date()
        transaction_type = transaction_type_input.lower()
        amount = float(amount_str)

        if transaction_type not in ["внести", "снять"]:
            bot.send_message(message.chat.id, "Неверный тип транзакции. Используйте 'внести' или 'снять'.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
                UPDATE transactions
                SET date = ?, card_name = ?, transaction_type = ?, amount = ?
                WHERE uuid = ?
                """, (date, card_name, transaction_type, amount, payment_uuid))
        conn.commit()
        conn.close()

        bot.send_message(message.chat.id, "Транзакция успешно обновлена!")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
        logging.error(f"Ошибка при редактировании транзакции: {str(e)}")


def edit_series_data(message, recurrence_id, bot):
    logging.info(f"Функция edit_series_data вызвана для recurrence_id: {recurrence_id}")
    try:
        inputs = message.text.strip().split()
        if len(inputs) != 4:
            bot.send_message(message.chat.id, "Неверное количество параметров. Введите: дата карта тип сумма.")
            return

        date_str, card_name, transaction_type_input, amount_str = inputs
        date = datetime.strptime(date_str, "%d.%m.%Y").date()
        transaction_type = transaction_type_input.lower()
        amount = float(amount_str)

        if transaction_type not in ["внести", "снять"]:
            bot.send_message(message.chat.id, "Неверный тип транзакции. Используйте 'внести' или 'снять'.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
                UPDATE transactions
                SET date = ?, card_name = ?, transaction_type = ?, amount = ?
                WHERE recurrence_id = ? AND date >= ?
                """, (date, card_name, transaction_type, amount, recurrence_id, datetime.now().date().isoformat()))
        conn.commit()
        conn.close()

        bot.send_message(message.chat.id, "Все транзакции в серии успешно обновлены!")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
        logging.error(f"Ошибка при редактировании серии транзакций: {str(e)}")


def update_transaction_status(uuid, status):
    conn = sqlite3.connect('transactions.db')
    cursor = conn.cursor()
    cursor.execute("""
                UPDATE transactions
                SET execution_status = ?
                WHERE UUID = ?
                """, (status, uuid))

    # Check if any rows were updated
    if cursor.rowcount == 0:
        logging.warning(f"Транзакция с UUID {uuid} не найдена для обновления.")
    else:
        logging.info(f"Транзакция с UUID {uuid} успешно обновлена.")

    conn.commit()  # Save changes
    conn.close()


def send_reminder_with_buttons(payment_uuid, message_text, transaction_type, bot, chat_id):
    """
    Функция отправляет напоминание с кнопкой для обновления статуса транзакции.

    Аргументы:
    payment_uuid -- идентификатор транзакции (UUID).
    message_text -- текст сообщения, который будет отправлен пользователю.
    transaction_type -- тип транзакции ("внести" или "снять").
    """

    # Создаем клавиатуру с кнопками
    markup = types.InlineKeyboardMarkup()

    # Добавляем соответствующую кнопку в зависимости от типа транзакции
    if transaction_type.lower() == "внести":
        button = types.InlineKeyboardButton("☑️ Уже внес", callback_data=f"done_{payment_uuid}")
    elif transaction_type.lower() == "снять":
        button = types.InlineKeyboardButton("✅ Уже снял", callback_data=f"withdrawn_{payment_uuid}")
    else:
        # Если тип транзакции неизвестен, используем универсальную кнопку "Выполнено"
        button = types.InlineKeyboardButton("✅ Выполнено", callback_data=f"done_{payment_uuid}")

    markup.add(button)

    # Логируем отправку напоминания для отладки
    logging.info(f"Отправка напоминания: '{message_text}' с кнопкой для UUID {payment_uuid}")

    # Пытаемся отправить сообщение с кнопкой
    try:
        bot.send_message(chat_id, message_text, reply_markup=markup)
        logging.info("Напоминание успешно отправлено.")
    except Exception as e:
        logging.error(f"Ошибка при отправке напоминания: {e}")


def send_reminders(bot, chat_id):
    logging.info('send_reminders запущен')

    current_datetime = datetime.now()
    current_date = current_datetime.date().isoformat()  # Форматируем текущую дату как строку 'YYYY-MM-DD'
    current_time_str = current_datetime.time().strftime("%H:%M")
    # reminder_today_times = ["10:00", "14:00", "17:00", "20:49"]
    # reminder_tomorrow_time = "15:00"

    # Подключаемся к базе данных и получаем все невыполненные транзакции
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
                SELECT * FROM '{chat_id}'
                WHERE execution_status = 0
                ORDER BY date ASC, transaction_type = 'снять'
                """)
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        payment_uuid = row['UUID']
        payment_date = row['date']  # Строка в формате 'YYYY-MM-DD'
        card_name = row['card_name']
        transaction_type = row['transaction_type']
        amount = row['amount']
        execution_status = row['execution_status']

        # Обработка transaction_type в нижнем регистре
        if isinstance(transaction_type, str):
            transaction_type_lower = transaction_type.lower()
        else:
            transaction_type_lower = ""
            logging.warning(f"Некорректный тип транзакции для UUID {payment_uuid}: {transaction_type}")

        # Проверка условий для отправки напоминания на сегодня
        if payment_date == current_date and current_time_str in reminder_today_times:
            logging.info(f'текущее время: {current_time_str}, время напоминания: {reminder_today_times}')
            message_text = f"‼️ Братишка, не шути так! Срочно: {amount:,.2f} руб. {transaction_type_lower} по карте {card_name}"
            send_reminder_with_buttons(payment_uuid, message_text, transaction_type_lower, bot, chat_id)

        # Проверка условий для отправки напоминания на завтра
        elif (payment_date == (datetime.fromisoformat(current_date) + timedelta(days=1)).isoformat() and
              current_time_str == reminder_tomorrow_time):
            message_text = f"⏰ Не забудь: Завтра {transaction_type_lower} {amount:,.2f} руб. по карте {card_name}"
            send_reminder_with_buttons(payment_uuid, message_text, transaction_type_lower, bot, chat_id)


def run_scheduler():
    while True:
        # Выполняем все запланированные задачи
        schedule.run_pending()

        # Определяем, сколько времени до следующего события
        next_run = schedule.idle_seconds()

        if next_run is None:
            # Если нет запланированных задач, делаем паузу на 1 минуту
            time.sleep(60)
        else:
            # Ждем до следующего запланированного события
            time.sleep(max(1, next_run))  # Ставим минимум 1 секунду ожидания


def safe_polling(bot):
    logging.info(f"Получен экземпляр бота: {bot}")
    while True:
        try:
            logging.info(f"Пытаемся запустить бота {bot}...")
            bot.polling(non_stop=True, interval=0, timeout=20)
            logging.info(f"Запуск бота {bot}")
        except Exception as e:
            logging.error(f"Ошибка: {e}, {bot}")  # Логируем ошибку
            if isinstance(e, telebot.apihelper.ApiException) and e.error_code == 403:
                logging.error("Бот был заблокирован пользователем.")
            logging.info("Перезапуск бота через 5 секунд...")
            logging.exception("Трассировка стека исключения:")
            time.sleep(5)
