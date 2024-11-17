import re

from db_functions import init_db
from remind_func import *
from functions import *
from keyboards import main_menu_keyboard, nearest_menu_keyboard, start_keyboard
from logger import logging
from settings import reccurent_count_months


def register_handlers(bot):
	@bot.message_handler(func=lambda message: message.text == "/start")
	def handle_start_button(message):
		# bot.send_message(message.chat.id, "Вы нажали кнопку 'Начать'!")
		user_chat_id = message.chat.id
		logging.info(f'id пользователя: {user_chat_id}')
		init_db(user_chat_id)
		logging.info('Таблица в БД активирована')
		run_reminders(bot, user_chat_id)
		logging.info(f'Запущен run_reminders для чата {user_chat_id}')
		logging.info(f'Пользователь {user_chat_id} запустил бота')
		markup = start_keyboard()
		bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}', reply_markup=markup)

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
			bot.send_message(message.chat.id, 'Пожалуйста, выберите действие из меню:',
							 reply_markup=main_menu_keyboard())

	# # @bot.callback_query_handler(
	# #     func=lambda call: call.data.startswith('delete_one_') or call.data.startswith('delete_series_'))
	# # def handle_delete_choice(call):
	# #     data = call.data
	# #     logging.info(f'Обработчик handle_delete_choice вызван с данными: {data}')
	# #     if data.startswith('delete_one_'):
	# #         payment_uuid = data.replace('delete_one_', '')
	# #         delete_one_transaction(payment_uuid)
	# #         bot.send_message(call.message.chat.id, 'Транзакция удалена.')
	# #     elif data.startswith('delete_series_'):
	# #         recurrence_id = data.replace('delete_series_', '')
	# #         delete_series(recurrence_id)
	# #         bot.send_message(call.message.chat.id, 'Вся серия транзакций удалена.')
	#
	# # @bot.callback_query_handler(func=lambda call: call.data.startswith('restore_series_'))
	# # def handle_restore_series(call):
	# #     recurrence_id = call.data.replace('restore_series_', '')
	# #     restore_transaction(recurrence_id=recurrence_id)
	# #     bot.send_message(call.message.chat.id, 'Вся серия транзакций восстановлена.')
	#
	# # Обработчик нажатия кнопки 'Отменить добавление'
	# @bot.callback_query_handler(func=lambda call: call.data == 'cancel_addition')
	# def handle_cancel_addition(call):
	#     # Очистка данных о добавляемой транзакции, если они есть
	#     if call.message.chat.id in payment_data:
	#         if 'last_payment_uuid' in payment_data[call.message.chat.id]:
	#             del payment_data[call.message.chat.id]['last_payment_uuid']
	#             logging.info(f'Процесс добавления транзакции отменен пользователем {call.message.chat.id}.')
	#
	#     # Очищаем шаг ожидания ввода данных
	#     bot.clear_step_handler(call.message)
	#
	#     # Уведомляем пользователя об отмене
	#     bot.send_message(call.message.chat.id, 'Процесс добавления транзакции отменен.')

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
		# Обработка выполнения транзакции
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
				bot.edit_message_reply_markup(
					chat_id=call.message.chat.id,
					message_id=call.message.message_id,
					reply_markup=markup
				)
				bot.answer_callback_query(call.id, 'Статус транзакции обновлён.')
			except Exception as e:
				logging.error(f'Ошибка при редактировании сообщения: {e}')
				bot.answer_callback_query(call.id, 'Не удалось обновить статус транзакции.')

		# Обработка отмены выполнения для напоминания или транзакции
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
					bot.edit_message_reply_markup(
						chat_id=call.message.chat.id,
						message_id=call.message.message_id,
						reply_markup=markup
					)
					bot.answer_callback_query(call.id, 'Отмена выполнена.')
				except Exception as e:
					logging.error(f'Ошибка при редактировании сообщения: {e}')
					bot.answer_callback_query(call.id, 'Не удалось отменить выполнение транзакции.')


		# Обработка отмены действия выполнения ('undo_')
		elif call.data.startswith('undo_done_'):
			# Извлекаем UUID для отмены
			payment_uuid = call.data.replace('undo_done_', '')
			update_transaction_status(payment_uuid, chat_id, 0)
			logging.info(f'Транзакция с UUID {payment_uuid} отменена.')

			# Восстановление начальных кнопок: выполнить или внести/снять
			markup = types.InlineKeyboardMarkup()
			done_button = types.InlineKeyboardButton('✅', callback_data=f'done_{payment_uuid}')
			withdrawn_button = types.InlineKeyboardButton('✅ Уже снял', callback_data=f'withdrawn_{payment_uuid}')
			markup.add(done_button, withdrawn_button)

			try:
				# Обновляем сообщение с кнопками
				bot.edit_message_reply_markup(
					chat_id=call.message.chat.id,
					message_id=call.message.message_id,
					reply_markup=markup
				)
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
				bot.edit_message_reply_markup(
					chat_id=call.message.chat.id,
					message_id=call.message.message_id,
					reply_markup=markup
				)
				bot.answer_callback_query(call.id, "Отметка отменена.")
			except Exception as e:
				logging.error(f"Ошибка при редактировании сообщения: {e}")
				bot.answer_callback_query(call.id, "Не удалось отменить отметку транзакции.")

		# Подтверждение удаления транзакции
		elif call.data.startswith("delete_"):
			payment_uuid = call.data.replace("delete_", "")

			markup = types.InlineKeyboardMarkup()
			confirm_button = types.InlineKeyboardButton("Да", callback_data=f"confirm_delete_{payment_uuid}")
			cancel_button = types.InlineKeyboardButton("Нет", callback_data="cancel_delete")
			markup.add(confirm_button, cancel_button)

			bot.send_message(call.message.chat.id, "Точно удалить эту транзакцию?", reply_markup=markup)

		elif call.data.startswith("delete_series_"):
			reccurence_id = call.data.replace("delete_series_", "")
			markup = types.InlineKeyboardMarkup()
			confirm_button = types.InlineKeyboardButton("Да", callback_data=f"confirm_delete_{reccurence_id}")
			cancel_button = types.InlineKeyboardButton("Нет", callback_data='cancel_delete')
			markup.add(confirm_button, cancel_button)

			bot.send_message(call.message.chat.id, "Удалить серию транзакций?", reply_markup=markup)

		# Удаление транзакции с возможностью отмены
		elif call.data.startswith("confirm_delete_"):
			payment_uuid = call.data.replace("confirm_delete_", "")

			# Удаление транзакции
			delete_transaction(payment_uuid, call.message.chat.id, bot)

			# Добавляем кнопку для отмены удаления
			markup = types.InlineKeyboardMarkup()
			undo_button = types.InlineKeyboardButton("❌ Отменить удаление", callback_data=f"undo_delete_{payment_uuid}")
			markup.add(undo_button)

			# Отправляем сообщение с кнопкой для отмены
			bot.send_message(call.message.chat.id, "Транзакция удалена. Вы можете отменить удаление:",
							 reply_markup=markup)

		# Отмена удаления транзакции
		elif call.data.startswith("undo_delete_"):
			payment_uuid = call.data.replace("undo_delete_", "")
			conn = get_db_connection()
			cursor = conn.cursor()

			# Проверяем, является ли транзакция частью серии
			cursor.execute(f"""SELECT recurrence_id FROM '{chat_id}' WHERE uuid = ?""", (payment_uuid,))
			result = cursor.fetchone()
			conn.close()

			if result and result['recurrence_id']:
				recurrence_id = result['recurrence_id']
				restore_transaction(chat_id, recurrence_id=recurrence_id)
				bot.send_message(call.message.chat.id, "Удаление отменено. Вся серия транзакций восстановлена.")
			else:
				restore_transaction(chat_id, uuid=payment_uuid)
				bot.send_message(call.message.chat.id, "Удаление отменено. Транзакция восстановлена.")


		# Отмена действия удаления
		elif call.data == "cancel_delete":
			bot.send_message(call.message.chat.id, "Удаление отменено.")

		# Редактирование транзакции
		elif call.data.startswith("edit_"):
			payment_uuid = call.data.split("_")[-1]
			logging.info(f"Получен UUID для редактирования: {payment_uuid}")

			# Проверка существования UUID
			transaction = get_transaction_by_uuid(payment_uuid, chat_id)
			if not transaction:
				bot.answer_callback_query(call.id, "Транзакция не найдена.")
				logging.error(f"Транзакция с UUID {payment_uuid} не найдена.")
				return

			# # Сохраняем UUID для редактирования
			# if call.from_user.id not in payment_data:
			#     payment_data[call.from_user.id] = {}
			# payment_data[call.from_user.id]['edit_uuid'] = payment_uuid

			# Получаем данные существующей транзакции для отображения пользователю
			payment_date = transaction['date']
			card_name = transaction['card_name']
			transaction_type = transaction['transaction_type']
			amount = transaction['amount']

			bot.send_message(
				call.message.chat.id,
				f"Редактируем транзакцию:\nДата: {payment_date}, Карта: {card_name}, Тип: {transaction_type}, Сумма: {amount}\n\nВведите новые данные в формате: дата карта тип сумма."
			)

			# Регистрация следующего шага для обработки новых данных
			bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_edit_payment,
													  bot=bot, payment_uuid=payment_uuid)

			# Добавляем кнопку "❌ Отменить редактирование"
			markup = types.InlineKeyboardMarkup()
			cancel_button = types.InlineKeyboardButton("❌ Отменить редактирование",
													   callback_data=f"cancel_edit_{payment_uuid}")
			markup.add(cancel_button)

			# Отправляем сообщение с кнопкой
			bot.send_message(call.message.chat.id, "Или нажмите кнопку ниже, чтобы выйти из режима редактирования:",
							 reply_markup=markup)

		# Отмена редактирования транзакции ГОТОВО
		elif call.data.startswith("cancel_edit_"):
			payment_uuid = call.data.replace("cancel_edit_", "")

			# Удаляем данные редактирования
			# if call.from_user.id in payment_data and 'edit_uuid' in payment_data[call.from_user.id]:
			# del payment_data[call.from_user.id]['edit_uuid']
			bot.clear_step_handler(call.message)  # Очищаем шаг ожидания ввода данных
			bot.send_message(call.message.chat.id, "Редактирование отменено.")
			main_menu_keyboard(call.message, bot)
		else:
			bot.answer_callback_query(call.id, "Редактирование не активно.")

	# @bot.callback_query_handler(func=lambda call: call.data in ["recurrence_yes", "recurrence_no"])
	# def update_existing_payment(payment_uuid, date, card_name, transaction_type, amount):
	#     logging.info(f"Начало обновления транзакции с UUID: {payment_uuid}")
	#
	#     # Подключение к базе данных SQLite
	#     conn = get_db_connection()
	#     cursor = conn.cursor()
	#
	#     # Обновляем запись в таблице transactions
	#     cursor.execute("""
	#         UPDATE transactions
	#         SET date = ?, card_name = ?, transaction_type = ?, amount = ?
	#         WHERE uuid = ?
	#     """, (date.isoformat(), card_name, transaction_type, amount, payment_uuid))
	#
	#     # Проверяем, была ли обновлена строка
	#     if cursor.rowcount == 0:
	#         logging.error(f"Транзакция с UUID {payment_uuid} не найдена для обновления.")
	#     else:
	#         logging.info(f"Транзакция с UUID {payment_uuid} успешно обновлена в базе данных.")
	#
	#     conn.commit()  # Сохраняем изменения в базе данных
	#     conn.close()  # Закрываем подключение
	#
	@bot.callback_query_handler(
		func=lambda call: call.data.startswith("edit_one_") or call.data.startswith("edit_series_"))
	def handle_edit_choice(call):
		chat_id = call.message.chat.id
		logging.info(f"Вызван обработчик handle_edit_choice с callback_data: {call.data}")
		data = call.data

		if data.startswith("edit_one_"):
			payment_uuid = data.replace("edit_one_", "")
			logging.info(f"Пытаемся найти транзакцию с UUID: {payment_uuid} без префиксов")
			transaction = find_transaction(payment_uuid, chat_id)

			if transaction:
				logging.info(f"Транзакция найдена для редактирования: {transaction}")
				bot.send_message(call.message.chat.id,
								 "Введите новые данные для редактирования этой транзакции в формате: дата карта тип сумма.")
				bot.register_next_step_handler(call.message, edit_transaction_data, payment_uuid)
			else:
				logging.warning(f"Транзакция для редактирования с UUID {payment_uuid} не найдена.")
				bot.send_message(call.message.chat.id, "Транзакция для редактирования не найдена.")

		elif data.startswith("edit_series_"):
			recurrence_id = data.replace("edit_series_", "")
			logging.info(f"Пытаемся найти серию транзакций с recurrence_id: {recurrence_id}")
			bot.send_message(call.message.chat.id,
							 "Введите новые данные для редактирования всей серии в формате: дата карта тип сумма.")
			bot.register_next_step_handler(call.message, edit_series_data, bot=bot, recurrence_id=recurrence_id,
										   chat_id=chat_id)
