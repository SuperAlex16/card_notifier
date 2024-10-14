import telebot
from telebot import types
from datetime import datetime, timedelta
import openpyxl
import schedule
import time
import threading
import os
from dotenv import load_dotenv
import logging
import uuid

# Загрузка переменных окружения из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования: DEBUG для более подробного
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

# Получение токена и chat_id из переменных окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

if not TOKEN:
    logging.error("Токен Telegram бота не установлен в файле .env.")
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен в файле .env.")

if not CHAT_ID:
    logging.error("CHAT_ID не установлен в файле .env.")
    raise ValueError("CHAT_ID не установлен в файле .env.")

try:
    CHAT_ID = int(CHAT_ID)  # Преобразование CHAT_ID в целое число
except ValueError:
    logging.error("CHAT_ID должен быть числом.")
    raise ValueError("CHAT_ID должен быть числом.")

bot = telebot.TeleBot(TOKEN)

# Загрузка файла Excel
try:
    workbook = openpyxl.load_workbook('Payments.xlsx')
    sheet = workbook.active
    logging.info("Файл Payments.xlsx успешно загружен.")
except FileNotFoundError:
    logging.error("Файл Payments.xlsx не найден.")
    raise

# Словарь для хранения промежуточных данных о новом платеже или редактируемом платеже
payment_data = {}

# Функция для получения сокращенного дня недели на русском языке
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

# Функция для создания клавиатуры главного меню
def main_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('📅 Что сегодня?')
    btn2 = types.KeyboardButton('🔜 Ближайшие')
    btn3 = types.KeyboardButton('➕ Добавить')
    btn4 = types.KeyboardButton('✏️ Редактировать')
    keyboard.add(btn1, btn2)
    keyboard.add(btn3, btn4)
    return keyboard

# Функция для создания клавиатуры подменю "Ближайшие"
def nearest_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('3️⃣ дня')
    btn2 = types.KeyboardButton('7️⃣ дней')
    btn3 = types.KeyboardButton('3️⃣0️⃣ дней')
    btn4 = types.KeyboardButton('🗓 Этот месяц')
    back = types.KeyboardButton('◀️ Назад')
    keyboard.add(btn1, btn2, btn3, btn4)
    keyboard.add(back)
    return keyboard

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = main_menu_keyboard()
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!', reply_markup=markup)
    logging.info(f"Пользователь {message.from_user.id} начал взаимодействие с ботом.")

# Обработчик основного меню и подменю "Ближайшие"
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    if message.text == "📅 Что сегодня?":
        show_today(message)
    elif message.text == "🔜 Ближайшие":
        bot.send_message(message.chat.id, "Выберите период:", reply_markup=nearest_menu_keyboard())
    elif message.text == "➕ Добавить":
        add_payment(message)
    elif message.text == "✏️ Редактировать":
        edit_payments(message)
    elif message.text == "3️⃣ дня":
        show_nearest_days(message, 3)
    elif message.text == "7️⃣ дней":
        show_nearest_days(message, 7)
    elif message.text == "3️⃣0️⃣ дней":
        show_nearest_days(message, 30)
    elif message.text == "🗓 Этот месяц":
        show_this_month(message)
    elif message.text == "◀️ Назад":
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=main_menu_keyboard())
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите действие из меню.", reply_markup=main_menu_keyboard())

# Функция для отображения платежей за сегодня
def show_today(message):
    current_date = datetime.now().date()
    payments_today = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        payment_uuid = row[0]
        payment_date = row[1].date() if isinstance(row[1], datetime) else None
        card_name = row[2]
        transaction_type = row[3]
        amount = row[4]
        execution_status = row[5]

        logging.debug(f"Проверка платежа: UUID={payment_uuid}, Дата={payment_date}, Карта={card_name}, Тип={transaction_type}, Сумма={amount}, Статус={execution_status}")

        if payment_date == current_date and execution_status == 0:
            weekday_short = get_weekday_short(payment_date)
            payment_str = f"{payment_date.strftime('%d.%m.%Y')} ({weekday_short}), {card_name}, {transaction_type}, {amount:,.2f} руб."
            payments_today.append({'uuid': payment_uuid, 'description': payment_str, 'type': transaction_type})

    if payments_today:
        for payment in payments_today:
            markup = types.InlineKeyboardMarkup()
            if payment['type'].lower() == "внести":
                button = types.InlineKeyboardButton("☑️ Уже внес", callback_data=f"done_{payment['uuid']}")
            elif payment['type'].lower() == "снять":
                button = types.InlineKeyboardButton("✅ Уже снял", callback_data=f"withdrawn_{payment['uuid']}")
            else:
                # Если тип транзакции неизвестен, можно добавить универсальную кнопку
                button = types.InlineKeyboardButton("✅ Выполнено", callback_data=f"done_{payment['uuid']}")
            markup.add(button)
            bot.send_message(message.chat.id, payment['description'], reply_markup=markup)
        logging.info(f"Отправлены платежи на сегодня пользователю {message.chat.id}.")
    else:
        bot.send_message(message.chat.id, "Нет платежей на сегодня.")
        logging.info(f"Платежей на сегодня нет. Информация отправлена пользователю {message.chat.id}.")

# Функция для отображения ближайших платежей за заданное количество дней
def show_nearest_days(message, days):
    current_date = datetime.now().date()
    date_limit = current_date + timedelta(days=days)
    payments = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        payment_uuid = row[0]
        payment_date = row[1].date() if isinstance(row[1], datetime) else None
        card_name = row[2]
        transaction_type = row[3]
        amount = row[4]
        execution_status = row[5]

        if payment_date and current_date < payment_date <= date_limit and execution_status == 0:
            weekday_short = get_weekday_short(payment_date)
            payment_str = f"{payment_date.strftime('%d.%m.%Y')} ({weekday_short}), {card_name}, {transaction_type}, {amount:,.2f} руб."
            payments.append({'uuid': payment_uuid, 'description': payment_str, 'type': transaction_type})

    if payments:
        for payment in payments:
            markup = types.InlineKeyboardMarkup()
            if payment['type'].lower() == "внести":
                button = types.InlineKeyboardButton("☑️ Уже внес", callback_data=f"done_{payment['uuid']}")
            elif payment['type'].lower() == "снять":
                button = types.InlineKeyboardButton("✅ Уже снял", callback_data=f"withdrawn_{payment['uuid']}")
            else:
                # Если тип транзакции неизвестен, можно добавить универсальную кнопку
                button = types.InlineKeyboardButton("✅ Выполнено", callback_data=f"done_{payment['uuid']}")
            markup.add(button)
            bot.send_message(message.chat.id, payment['description'], reply_markup=markup)
        logging.info(f"Отправлены платежи за следующие {days} дней пользователю {message.chat.id}.")
    else:
        bot.send_message(message.chat.id, f"Нет платежей за следующие {days} дней.")
        logging.info(f"Платежей за следующие {days} дней нет. Информация отправлена пользователю {message.chat.id}.")

# Функция для отображения платежей за текущий месяц
def show_this_month(message):
    current_date = datetime.now().date()
    current_month = current_date.month
    current_year = current_date.year
    payments = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        payment_uuid = row[0]
        payment_date = row[1].date() if isinstance(row[1], datetime) else None
        card_name = row[2]
        transaction_type = row[3]
        amount = row[4]
        execution_status = row[5]

        if (payment_date and payment_date.month == current_month and
            payment_date.year == current_year and
            payment_date >= current_date and
            execution_status == 0):
            weekday_short = get_weekday_short(payment_date)
            payment_str = f"{payment_date.strftime('%d.%m.%Y')} ({weekday_short}), {card_name}, {transaction_type}, {amount:,.2f} руб."
            payments.append({'uuid': payment_uuid, 'description': payment_str, 'type': transaction_type})

    if payments:
        for payment in payments:
            markup = types.InlineKeyboardMarkup()
            if payment['type'].lower() == "внести":
                button = types.InlineKeyboardButton("☑️ Уже внес", callback_data=f"done_{payment['uuid']}")
            elif payment['type'].lower() == "снять":
                button = types.InlineKeyboardButton("✅ Уже снял", callback_data=f"withdrawn_{payment['uuid']}")
            else:
                # Если тип транзакции неизвестен, можно добавить универсальную кнопку
                button = types.InlineKeyboardButton("✅ Выполнено", callback_data=f"done_{payment['uuid']}")
            markup.add(button)
            bot.send_message(message.chat.id, payment['description'], reply_markup=markup)
        logging.info(f"Отправлены платежи за текущий месяц пользователю {message.chat.id}.")
    else:
        bot.send_message(message.chat.id, "Нет платежей за текущий месяц.")
        logging.info(f"Платежей за текущий месяц нет. Информация отправлена пользователю {message.chat.id}.")

# Функция добавления платежа
def add_payment(message):
    bot.send_message(
        message.chat.id,
        "Введите дату (дд.мм.гггг), название карты, 'внести' или 'снять', сумму через пробел:",
        reply_markup=types.ForceReply(selective=False)
    )
    bot.register_next_step_handler(message, process_payment_data)
    logging.info(f"Пользователь {message.chat.id} инициировал добавление платежа.")

# Функция обработки введенных данных платежа
def process_payment_data(message):
    try:
        inputs = message.text.strip().split()
        if len(inputs) != 4:
            raise ValueError("Неверное количество параметров.")

        date_str, card_name, transaction_type_input, amount_str = inputs
        date = datetime.strptime(date_str, "%d.%m.%Y").date()
        transaction_type = transaction_type_input.lower()
        amount = float(amount_str)

        if transaction_type not in ["внести", "снять"]:
            raise ValueError("Неверный тип транзакции. Используйте 'внести' или 'снять'.")

        # Генерация UUID для нового платежа
        payment_uuid = str(uuid.uuid4())

        # Проверяем, является ли текущая операция редактированием
        if message.chat.id in payment_data and 'edit_uuid' in payment_data[message.chat.id]:
            old_uuid = payment_data[message.chat.id]['edit_uuid']
            # Добавление нового платежа
            sheet.append([
                payment_uuid,
                datetime.combine(date, datetime.min.time()),
                card_name,
                transaction_type,
                amount,
                0  # Execution status
            ])
            logging.info(f"Добавлен новый платеж с UUID {payment_uuid} для пользователя {message.chat.id} (редактирование).")

            # Удаление старого платежа
            remove_payment_by_uuid(old_uuid)
            logging.info(f"Удален старый платеж с UUID {old_uuid} после редактирования.")

            # Очистка данных редактирования
            del payment_data[message.chat.id]['edit_uuid']
        else:
            # Добавление нового платежа
            sheet.append([
                payment_uuid,
                datetime.combine(date, datetime.min.time()),
                card_name,
                transaction_type,
                amount,
                0  # Execution status
            ])
            logging.info(f"Добавлен новый платеж с UUID {payment_uuid} для пользователя {message.chat.id}.")

        workbook.save('Payments.xlsx')

        # Восстановление главного меню
        bot.send_message(message.chat.id, "Платеж(и) добавлен(ы)!", reply_markup=main_menu_keyboard())
        logging.info(f"Платеж(и) успешно добавлен(ы) для пользователя {message.chat.id}.")
    except (ValueError, IndexError) as e:
        bot.send_message(message.chat.id, "Ошибка. Пожалуйста, проверьте формат ввода.")
        logging.error(f"Ошибка при обработке данных платежа от пользователя {message.chat.id}: {e}")

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

    for row in sheet.iter_rows(min_row=2, values_only=True):
        payment_uuid = row[0]
        payment_date = row[1].date() if isinstance(row[1], datetime) else None
        card_name = row[2]
        transaction_type = row[3]
        amount = row[4]
        execution_status = row[5]

        if payment_date and current_date <= payment_date <= date_limit and execution_status == 0:
            weekday_short = get_weekday_short(payment_date)
            payment_str = f"{payment_date.strftime('%d.%m.%Y')} ({weekday_short}), {card_name}, {transaction_type}, {amount:,.2f} руб."
            payments.append({'uuid': payment_uuid, 'description': payment_str, 'type': transaction_type})

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
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    data = call.data
    logging.debug(f"Получен callback_data: {data} от пользователя {call.from_user.id}")

    if data.startswith("done_") or data.startswith("withdrawn_"):
        action, payment_uuid = data.split("_", 1)
        try:
            # Проверяем существование UUID
            if not any(row[0].value == payment_uuid for row in sheet.iter_rows(min_row=2, values_only=False)):
                raise ValueError("UUID не найден.")
        except Exception as e:
            logging.error(f"Ошибка при поиске UUID {payment_uuid}: {e}")
            bot.answer_callback_query(call.id, "Платеж не найден.")
            return

        # Обновление статуса платежа на 1
        update_payment_status(payment_uuid, 1)
        logging.info(f"Платеж с UUID {payment_uuid} отмечен как выполненный/снятый.")

        # Определение нового текста и callback_data для кнопки
        if action == "done":
            new_button_text = "Готово. Отменить?"
            new_callback_data = f"undo_done_{payment_uuid}"
        elif action == "withdrawn":
            new_button_text = "Готово. Отменить?"
            new_callback_data = f"undo_withdrawn_{payment_uuid}"
        else:
            new_button_text = "✅ Выполнено"
            new_callback_data = f"done_{payment_uuid}"

        # Обновление кнопки в сообщении
        markup = types.InlineKeyboardMarkup()
        undo_button = types.InlineKeyboardButton(new_button_text, callback_data=new_callback_data)
        markup.add(undo_button)

        try:
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id, "Статус платежа обновлён.")
        except Exception as e:
            logging.error(f"Ошибка при редактировании сообщения: {e}")
            bot.answer_callback_query(call.id, "Не удалось обновить статус платежа.")

    elif data.startswith("undo_done_") or data.startswith("undo_withdrawn_"):
        parts = data.split("_")
        if len(parts) != 3:
            logging.error(f"Неверный формат callback_data для отмены: {data}")
            bot.answer_callback_query(call.id, "Неверный формат данных.")
            return

        _, action_type, payment_uuid = parts
        try:
            # Проверяем существование UUID
            if not any(row[0].value == payment_uuid for row in sheet.iter_rows(min_row=2, values_only=False)):
                raise ValueError("UUID не найден.")
        except Exception as e:
            logging.error(f"Ошибка при поиске UUID {payment_uuid}: {e}")
            bot.answer_callback_query(call.id, "Платеж не найден.")
            return

        # Обновление статуса платежа на 0
        update_payment_status(payment_uuid, 0)
        logging.info(f"Платеж с UUID {payment_uuid} отменён.")

        # Определение нового текста и callback_data для кнопки
        if data.startswith("undo_done_"):
            original_action = "done"
            new_button_text = "☑️ Уже внес"
            new_callback_data = f"done_{payment_uuid}"
        elif data.startswith("undo_withdrawn_"):
            original_action = "withdrawn"
            new_button_text = "✅ Уже снял"
            new_callback_data = f"withdrawn_{payment_uuid}"
        else:
            original_action = "done"
            new_button_text = "✅ Выполнено"
            new_callback_data = f"done_{payment_uuid}"

        # Обновление кнопки в сообщении
        markup = types.InlineKeyboardMarkup()
        original_button = types.InlineKeyboardButton(new_button_text, callback_data=new_callback_data)
        markup.add(original_button)

        try:
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id, "Отметка об отмене выполнена.")
        except Exception as e:
            logging.error(f"Ошибка при редактировании сообщения: {e}")
            bot.answer_callback_query(call.id, "Не удалось отменить отметку платежа.")
    elif data.startswith("edit_"):
        payment_uuid = data.split("_", 1)[1]
        # Проверяем существование UUID
        if not any(row[0].value == payment_uuid for row in sheet.iter_rows(min_row=2, values_only=False)):
            bot.answer_callback_query(call.id, "Платеж не найден.")
            logging.error(f"Платеж с UUID {payment_uuid} не найден.")
            return

        # Сохраняем UUID для редактирования
        if call.from_user.id not in payment_data:
            payment_data[call.from_user.id] = {}
        payment_data[call.from_user.id]['edit_uuid'] = payment_uuid

        bot.send_message(call.message.chat.id, "Редактируйте платеж, введя новые данные:")
        bot.send_message(
            call.message.chat.id,
            "Введите дату (дд.мм.гггг), название карты, 'внести' или 'снять', сумму через пробел:",
            reply_markup=types.ForceReply(selective=False)
        )
        bot.register_next_step_handler(call.message, process_payment_data)
        logging.info(f"Пользователь {call.from_user.id} начал редактирование платежа с UUID {payment_uuid}.")
    else:
        bot.answer_callback_query(call.id, "Неизвестное действие.")
        logging.warning(f"Неизвестный callback_data: {data}")

# Функция для обновления статуса платежа
def update_payment_status(payment_uuid, status):
    date_found = False
    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row):
        cell = row[0]
        if cell.value == payment_uuid:
            row[5].value = status  # Обновляем статус
            date_found = True
            logging.debug(f"UUID {payment_uuid}: Статус обновлён на {status}.")
            break

    if date_found:
        try:
            workbook.save('Payments.xlsx')
            logging.info(f"Файл Payments.xlsx сохранён после обновления UUID {payment_uuid}.")
        except Exception as e:
            logging.error(f"Ошибка при сохранении файла Payments.xlsx: {e}")
    else:
        logging.warning(f"Платеж с UUID {payment_uuid} не найден для обновления статуса.")

# Функция для отправки напоминаний с кнопками
def send_reminder_with_buttons(payment_uuid, message_text, transaction_type):
    markup = types.InlineKeyboardMarkup()
    if transaction_type.lower() == "внести":
        button = types.InlineKeyboardButton("☑️ Уже внес", callback_data=f"done_{payment_uuid}")
    elif transaction_type.lower() == "снять":
        button = types.InlineKeyboardButton("✅ Уже снял", callback_data=f"withdrawn_{payment_uuid}")
    else:
        # Универсальная кнопка, если тип транзакции неизвестен
        button = types.InlineKeyboardButton("✅ Выполнено", callback_data=f"done_{payment_uuid}")
    markup.add(button)

    logging.info(f"Отправка напоминания: '{message_text}' с кнопкой для UUID {payment_uuid}")
    try:
        bot.send_message(CHAT_ID, message_text, reply_markup=markup)
    except Exception as e:
        logging.error(f"Ошибка при отправке напоминания: {e}")

# Функция для отправки напоминаний
def send_reminders():
    current_datetime = datetime.now()
    current_date = current_datetime.date()
    current_time = current_datetime.time()
    current_time_str = current_time.strftime("%H:%M")

    reminder_today_times = ["10:00", "14:00", "17:00"]
    reminder_tomorrow_time = "15:00"

    for row in sheet.iter_rows(min_row=2, values_only=True):
        payment_uuid = row[0]
        payment_date = row[1].date() if isinstance(row[1], datetime) else None
        card_name = row[2]
        transaction_type = row[3]
        amount = row[4]
        execution_status = row[5]

        if payment_date and execution_status == 0:
            # Обработка transaction_type
            if isinstance(transaction_type, str):
                transaction_type_lower = transaction_type.lower()
            else:
                transaction_type_lower = ""
                logging.warning(f"Некорректный тип транзакции для UUID {payment_uuid}: {transaction_type}")

            if payment_date == current_date and current_time_str in reminder_today_times:
                message_text = f"Напоминание: Платеж на {payment_date.strftime('%d.%m.%Y')} ({get_weekday_short(payment_date)}), {card_name}, {transaction_type_lower}, {amount:,.2f} руб."
                send_reminder_with_buttons(payment_uuid, message_text, transaction_type_lower)
            elif (payment_date == current_date + timedelta(days=1) and
                  current_time_str == reminder_tomorrow_time and
                  execution_status == 0):
                message_text = f"Напоминание: Завтра платеж на {payment_date.strftime('%d.%m.%Y')} ({get_weekday_short(payment_date)}), {card_name}, {transaction_type_lower}, {amount:,.2f} руб."
                send_reminder_with_buttons(payment_uuid, message_text, transaction_type_lower)

# Функция для безопасного запуска бота с обработкой исключений
def safe_polling():
    while True:
        try:
            logging.info("Запуск бота.")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            logging.error(f"Ошибка в bot.polling: {e}")
            logging.info("Перезапуск бота через 5 секунд.")
            time.sleep(5)

# Функция для запуска планировщика в отдельном потоке
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Запланировать отправку напоминаний каждые 5 минут
schedule.every(5).minutes.do(send_reminders)
logging.info("Запланирована отправка напоминаний каждые 5 минут.")

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()
logging.info("Планировщик запущен в отдельном потоке.")

# Запуск бота
safe_polling()
