import sqlite3

from logger import logging
from settings import db_file


# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect(db_file)  # Открывает или создает файл базы данных 'transactions.db'
    conn.row_factory = sqlite3.Row  # Позволяет обращаться к полям результата запроса по именам колонок
    return conn


# Функция для создания таблицы транзакций
def init_db(chat_id):
    table_name = chat_id
    logging.info(f'Инициализация базы данных для чата: {table_name}...')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS "{table_name}" (
                UUID             TEXT              NOT NULL PRIMARY KEY,
                date             TEXT              NOT NULL,
                card_name        TEXT              NOT NULL,
                transaction_type TEXT              NOT NULL,
                amount           REAL              NOT NULL,
                execution_status INTEGER DEFAULT 0 NOT NULL,
                recurrence_id    TEXT,
                is_recursive     INTEGER DEFAULT 0,
                is_active        INT DEFAULT 1 NOT NULL
            )
        """)
        conn.commit()

        cursor.execute(f"""
            SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';
        """)
        result = cursor.fetchone()

        if result:
            logging.info(f'Таблица "{table_name}" существует или была успешно создана')
        else:
            logging.warning(f'Таблица "{table_name}" НЕ была создана')

    except Exception as e:
        logging.error(f'Ошибка при инициализации БД для чата {table_name}: {e}')

    finally:
        if conn:
            conn.close()
            logging.info(f'Соединение с БД закрыто')
