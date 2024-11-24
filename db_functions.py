import sqlite3

from logger import logging
from settings import db_file


def get_db_connection():
    logging.info(f"Connecting to db: {db_file}...")
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        logging.info(f"Connected to db: {db_file}")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Failed to connect to {db_file}: {e}")


def init_db(chat_id):
    table_name = chat_id
    logging.info(f"Creating a table for chat_id: {table_name}...")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS "{table_name}" (
                UUID             TEXT              NOT NULL PRIMARY KEY,
                date             TEXT              NOT NULL,
                card_name        TEXT              NOT NULL,
                transaction_type TEXT              NOT NULL,
                amount           REAL              NOT NULL,
                execution_status INTEGER DEFAULT 0 NOT NULL,
                recurrence_id    TEXT,
                is_active        INT DEFAULT 1 NOT NULL
            )
        """
            )
        conn.commit()

        cursor.execute(
            f"""
            SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';
        """
            )
        result = cursor.fetchone()

        if result:
            logging.info(f"Table {table_name} exists or was created successfully")
        else:
            logging.warning(f"Table {table_name} was NOT created")

    except Exception as e:
        logging.error(f"Error while opening a table {table_name}: {e}")

    finally:
        if conn:
            conn.close()
            logging.info(f'Connection closed for chat_id: {table_name}')
