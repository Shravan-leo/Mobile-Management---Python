from idlelib import query

import mysql.connector
import select


def get_connection():
    return  mysql.connector.connect(
        host="localhost",
        user="root",
        password="csk123",
        database="mobile_db",
    )


def ensure_file_data_column():
    """Add file_data only when it does not already exist."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s
              AND TABLE_NAME = %s
              AND COLUMN_NAME = %s
        """, ("mobile_db", "models", "file_data"))

        column_exists = cursor.fetchone()[0] > 0

        if not column_exists:
            cursor.execute("""
                ALTER TABLE models
                ADD COLUMN file_data LONGBLOB NULL
            """)
            connection.commit()
            print("file_data column added successfully.")
        else:
            print("file_data column already exists.")

        cursor.close()

    finally:
        connection.close()


def save_pdf_to_model(model_id: int, pdf_bytes: bytes):
    """Store PDF binary data against an existing model ID."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE models
            SET file_data = %s
            WHERE id = %s
        """, (pdf_bytes, model_id))

        if cursor.rowcount == 0:
            connection.rollback()
            return False

        connection.commit()
        return True

    finally:
        cursor.close()
        connection.close()


def get_pdf_from_model(model_id: int):
    """Retrieve the stored PDF binary data."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT file_data
            FROM models
            WHERE id = %s
        """, (model_id,))

        result = cursor.fetchone()

        if result is None:
            return None

        return result[0]

    finally:
        cursor.close()
        connection.close()

def get_models():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
            SELECT id, name, price
            FROM models
            ORDER BY id ASC 
            """
    cursor.execute(query)
    models = cursor.fetchall()
    cursor.close()
    connection.close()

    return {
        "Success:": True,
        "Status code": 200,
        "Message:": "Mobile models fetched successfully!",
        "data": models
    }


def get_all_models():
    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                m.id,
                m.name,
                m.price,
                d.device_id,
                d.device_name
            FROM models m
            LEFT JOIN device d
                ON m.id = d.model_id
            ORDER BY m.id ASC, d.device_id ASC
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        models_dict = {}

        for row in rows:
            model_id = row["id"]

            if model_id not in models_dict:
                models_dict[model_id] = {
                    "id": row["id"],
                    "name": row["name"],
                    "price": row["price"],
                    "device_names": []
                }

            if row["device_name"] is not None:
                models_dict[model_id]["device_names"].append(
                    row["device_name"]
                )

        return {
            "success": True,
            "status_code": 200,
            "message": "Mobile models fetched successfully!",
            "data": list(models_dict.values())
        }

    finally:
        cursor.close()
        connection.close()



def insert_models(model):
    connection = get_connection()
    cursor = connection.cursor()
    query = "insert into models (id,name, price) values (%s, %s, %s)"
    cursor.execute(query, (model.id,model.name,model.price) )
    connection.commit()
    cursor.close()
    connection.close()
    return {
        "Success:": True,
        "Message:": "Mobile models inserted successfully!",
        "data": model
    }

def delete_model_by_id(model_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    query = "delete from models where id = %s"
    cursor.execute(query, (model_id,) )
    connection.commit()
    cursor.close()
    connection.close()
    return {
        "Success:": True,
        "Message:": "Mobile model deleted successfully!",
    }