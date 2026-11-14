
from modules.database import get_connection


def save_analysis(user_id, file_name, df, report_text):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO analysis_history (
                user_id,
                file_name,
                total_rows,
                total_columns,
                missing_values,
                duplicate_rows,
                report_text
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            file_name,
            int(df.shape[0]),
            int(df.shape[1]),
            int(df.isnull().sum().sum()),
            int(df.duplicated().sum()),
            report_text
        ))

        connection.commit()
        return True

    finally:
        cursor.close()
        connection.close()


def get_user_history(user_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                id,
                file_name,
                total_rows,
                total_columns,
                missing_values,
                duplicate_rows,
                created_at
            FROM analysis_history
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_history_report(user_id, history_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT report_text
            FROM analysis_history
            WHERE user_id = %s AND id = %s
        """, (user_id, history_id))

        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()
