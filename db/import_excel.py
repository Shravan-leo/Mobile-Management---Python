import pandas as pd
import mysql.connector
from pathlib import Path

# Excel file is stored in the same directory as this Python script
excel_file = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "mobile_models.xlsx"
)

# Check whether the file exists
if not excel_file.exists():
    raise FileNotFoundError(
        f"Excel file not found: {excel_file}"
    )

# Read Excel data
df = pd.read_excel(excel_file)

# Validate required columns
required_columns = {"id", "name", "price"}

if not required_columns.issubset(df.columns):
    raise ValueError(
        f"Excel file must contain these columns: {required_columns}"
    )

# Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="csk123",
    database="mobile_db",
)

cursor = connection.cursor()
# Clear existing records
cursor.execute("DELETE FROM models")

query = """
    INSERT INTO models (id, name, price)
    VALUES (%s, %s, %s)
"""

try:
    data = [
        (int(row.id), str(row.name), int(row.price))
        for row in df.itertuples(index=False)
    ]

    cursor.executemany(query, data)
    connection.commit()

    print(f"Successfully inserted {cursor.rowcount} records.")

except Exception as error:
    connection.rollback()
    print("Error inserting records:", error)

finally:
    cursor.close()
    connection.close()