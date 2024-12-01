import sqlite3

from log.logger import logging
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
        return None


def init_db(chat_id):
    table_name = str(chat_id)
    logging.info(f"Creating a table for chat_id: {table_name}...")

    conn = get_db_connection()
    if conn is None:
        logging.error(f"Unable to connect to database {db_file} for {table_name}")
        return

    with conn:
        try:
            cursor = conn.cursor()
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
        except sqlite3.Error as e:
            logging.error(f"Error while executing SQL for table {table_name}: {e}")
