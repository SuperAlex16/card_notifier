import sqlite3


from settings import db_file

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect(db_file)  # Открывает или создает файл базы данных 'transactions.db'
    conn.row_factory = sqlite3.Row  # Позволяет обращаться к полям результата запроса по именам колонок
    return conn

# Функция для создания таблицы транзакций
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            uuid TEXT PRIMARY KEY,
            date TEXT,
            card_name TEXT,
            transaction_type TEXT,
            amount REAL,
            execution_status INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# Функция для создания таблицы удаленных транзакций
def init_deleted_transactions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deleted_transactions (
            uuid TEXT PRIMARY KEY,
            date TEXT,
            card_name TEXT,
            transaction_type TEXT,
            amount REAL,
            execution_status INTEGER
        )
    """)
    conn.commit()
    conn.close()