from func.db_functions import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
try:

    # Getting all user's tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name GLOB '[0-9]*';")
    user_tables = [row[0] for row in cursor.fetchall()]
    print(f"User tables found: {user_tables}\nTotal: {len(user_tables)} tables")

    # Creating new table "transactions"
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            UUID             TEXT PRIMARY KEY NOT NULL,
            user_id          TEXT NOT NULL,
            date             TEXT NOT NULL,
            card_name        TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            amount           REAL NOT NULL,
            execution_status INTEGER DEFAULT 0 NOT NULL,
            recurrence_id    TEXT,
            is_active        INTEGER DEFAULT 1 NOT NULL
        );
        """
    )
    print("'transactions' table created successfully.")

    # Transferring data from user's tables to "transactions"
    for table in user_tables:
        user_id = table  # Имя таблицы равно user_id
        print(f"Transferring data from table '{table}' to transactions...")
        cursor.execute(
            f"""
            INSERT INTO transactions (UUID, user_id, date, card_name, transaction_type, amount, execution_status, recurrence_id, is_active)
            SELECT UUID, ?, date, card_name, transaction_type, amount, execution_status, recurrence_id, is_active
            FROM "{table}";
            """, (user_id,)
        )
    conn.commit()
    print("Data successfully transferred to 'transactions'.")

    # Delete user's tables  #
    for table in user_tables:
        print(f"Dropping table '{table}'...")
        cursor.execute(f"DROP TABLE IF EXISTS \"{table}\";")
        conn.commit()
    print("User tables successfully dropped.")

finally:
    # Close connection
    cursor.close()
    conn.close()
    print("Database connection closed.")
    print("Migrations complete.")
