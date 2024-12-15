from func.db_functions import get_db_connection
from log.logger import logging


def delete_transactions(chat_id, payment_id=None, recurrence_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if recurrence_id:
            cursor.execute(
                """
                UPDATE transactions
                SET is_active = 0
                WHERE user_id = ? AND recurrence_id = ?;
                """, (chat_id, recurrence_id)
            )

            conn.commit()

        elif payment_id:
            cursor.execute(
                """
                        UPDATE transactions 
                        SET is_active = 0 
                        WHERE user_id = ? AND UUID = ?
                        """, (chat_id, payment_id,)
            )
            conn.commit()
    except Exception as e:
        logging.error(f"{e}")
    finally:
        conn.close()


def undo_delete_transactions(chat_id, payment_id=None, recurrence_id=None, ):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if recurrence_id:
            cursor.execute(
                f"""
                        UPDATE transactions
                        SET is_active = 1 
                        WHERE user_id = ? AND recurrence_id = ?
                        """, (chat_id, recurrence_id,)
            )
            conn.commit()

        elif payment_id:
            cursor.execute(
                f"""
                        UPDATE transactions 
                        SET is_active = 1 
                        WHERE user_id = ? AND UUID = ?
                        """, (chat_id, payment_id,)
            )
            conn.commit()
    except Exception as e:
        logging.error(f"{e}")
    finally:
        conn.close()


def done_transactions(chat_id, payment_uuid=None, recurrence_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if recurrence_id:
            cursor.execute(
                f"""
                            UPDATE transactions
                            SET execution_status = 1, is_active = 0
                            WHERE user_id = ? AND recurrence_id = ?
                            """, (chat_id, recurrence_id,)
            )
            conn.commit()

        elif payment_uuid:
            cursor.execute(
                f"""
                            UPDATE transactions 
                            SET execution_status = 1, is_active = 0 
                            WHERE user_id = ? AND UUID = ?
                            """, (chat_id, payment_uuid,)
            )
            conn.commit()
    except Exception as e:
        logging.error(f"{e}")
    finally:
        conn.close()


def undone_transactions(chat_id, payment_uuid=None, recurrence_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if recurrence_id:
            cursor.execute(
                f"""
                            UPDATE transactions
                            SET execution_status = 0, is_active = 1
                            WHERE user_id = ? AND recurrence_id = ?
                            """, (chat_id, recurrence_id,)
            )
            conn.commit()

        elif payment_uuid:
            cursor.execute(
                f"""
                            UPDATE transactions 
                            SET execution_status = 0, is_active = 1
                            WHERE user_id = ? AND UUID = ?
                            """, (chat_id, payment_uuid,)
            )
            conn.commit()
    except Exception as e:
        logging.error(f"{e}")
    finally:
        conn.close()
