### TODO переделать настройки через ini-файл для изменения без перезапуска бота (либо найти другой метод реализации)

db_file = "transactions.db"

main_menu_keyboard_text = {
    1: "📅 Что сегодня?",
    2: "🔜 Ближайшие",
    3: "➕ Добавить",
    4: "✏️ Редактировать"
}

nearest_menu_keyboard_text = {
    1: "3️⃣ дня",
    2: "7️⃣ дней",
    3: "3️⃣0️⃣ дней",
    4: "🗓 Этот месяц",
    5: "◀️ Назад"
}

reminder_period = 1

reminder_today_times = ["10:00", "14:00", "17:00", "23:09"]
reminder_tomorrow_times = "18:40"

recurrent_count_months = 36

db_transaction_types = {
    1: "внести",
    2: "снять"
}

date_format = "%d/%m/%Y"
