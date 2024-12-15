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
