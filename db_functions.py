from logger import logging
import sqlite3

from settings import db_file


# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect(db_file)  # Открывает или создает файл базы данных 'transactions.db'
    conn.row_factory = sqlite3.Row  # Позволяет обращаться к полям результата запроса по именам колонок
    return conn


# Функция для создания таблицы транзакций
def init_db(chat_id):
    table_name = chat_id
    logging.info(f'table_name: {table_name}')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            UUID             TEXT              not null
        primary key,
    date             TEXT              not null,
    card_name        TEXT              not null,
    transaction_type TEXT              not null,
    amount           REAL              not null,
    execution_status INTEGER default 0 not null,
    recurrence_id    TEXT,
    is_recursive     INTEGER default 0,
    is_active        INT     default 1 not null
        )
    """)
    conn.commit()
    conn.close()
