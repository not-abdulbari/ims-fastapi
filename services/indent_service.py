import os
import re
import pandas as pd
from mysql.connector import connect, Error

# Load environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "ims_db")


# Establish database connection
def get_db_connection():
    try:
        return connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD if DB_PASSWORD else None,  # handle empty password
            database=DB_NAME
        )
    except Error as e:
        raise Exception(f"Database connection failed: {e}")


# Helper function to extract weight and pieces details
def extract_details(product_name, requested_quantity):
    """
    Extracts min_weight, max_weight, unit, and pieces from product name.
    Scales weights and piece count by requested_quantity.
    Handles formats like:
        - (400 - 600 gm)
        - 400 gm - 600 gm
        - 500 gm
        - 3 Units
        - 5 Pieces
    """
    min_weight, max_weight, unit = None, None, None
    pieces = None
    product_name_lower = product_name.lower()

    # Pattern 1: (X - Y gm/kg) → e.g., (400 - 600 gm)
    bracket_range = re.search(r"\(\s*([\d.]+)\s*-\s*([\d.]+)\s*(?:gm|g|kg)\s*\)", product_name_lower)

    # Pattern 2: X gm - Y gm → e.g., 400 gm - 600 gm
    dual_unit_range = re.search(r"([\d.]+)\s*(gm|g|kg)\s*-\s*([\d.]+)\s*(?:gm|g|kg)", product_name_lower)

    # Pattern 3: X - Y gm → e.g., 400 - 600 gm
    simple_range = re.search(r"([\d.]+)\s*-\s*([\d.]+)\s*(gm|g|kg)", product_name_lower)

    # Pattern 4: Single weight → e.g., 500 gm
    single_value = re.search(r"([\d.]+)\s*(gm|g|kg)", product_name_lower)

    # Pattern 5: Numeric Units → e.g., "3 Units", "5 Pieces"
    num_units = re.search(r"(\d+)\s*(units?|pieces?)", product_name_lower)

    if bracket_range:
        min_val = float(bracket_range.group(1))
        max_val = float(bracket_range.group(2))
        unit = "g"
        min_weight = min_val * requested_quantity
        max_weight = max_val * requested_quantity

    elif dual_unit_range:
        min_val = float(dual_unit_range.group(1))
        max_val = float(dual_unit_range.group(3))
        unit = dual_unit_range.group(2)
        min_weight = min_val * requested_quantity
        max_weight = max_val * requested_quantity

    elif simple_range:
        min_val = float(simple_range.group(1))
        max_val = float(simple_range.group(2))
        unit = simple_range.group(3)
        min_weight = min_val * requested_quantity
        max_weight = max_val * requested_quantity

    elif single_value:
        val = float(single_value.group(1))
        unit_str = single_value.group(2)
        min_weight = val * requested_quantity
        max_weight = None
        unit = unit_str

    elif num_units:
        unit_count = int(num_units.group(1))
        pieces = unit_count * requested_quantity
        unit = "Unit"

    elif "unit" in product_name_lower or "piece" in product_name_lower:
        unit = "Unit"

    # Normalize unit
    if unit in ["gm", "g"]:
        unit = "g"
    elif unit == "kg":
        unit = "kg"

    return min_weight, max_weight, unit, pieces


# Upload indent logic
def upload_indent(file, date, store_name):
    try:
        # Read the .xlsx file
        df = pd.read_excel(file.file)

        # Validate required columns
        required_columns = {"Product Number", "Product Name", "Requested Quantity"}
        if not required_columns.issubset(df.columns):
            return {"error": f"Missing required columns. Required: {required_columns}"}

        # Apply extraction to DataFrame
        df["Min Weight"], df["Max Weight"], df["Unit"], df["Pieces"] = zip(
            *df.apply(
                lambda row: extract_details(row["Product Name"], row["Requested Quantity"]),
                axis=1
            )
        )

        # Insert data into the database
        connection = get_db_connection()
        cursor = connection.cursor()

        insert_query = """
            INSERT INTO indent 
            (product_number, product_name, requested_quantity, min_weight, max_weight, unit, pieces, date, store_name) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for _, row in df.iterrows():
            cursor.execute(
                insert_query,
                (
                    row["Product Number"],
                    row["Product Name"],
                    row["Requested Quantity"],
                    row["Min Weight"],
                    row["Max Weight"],
                    row["Unit"],
                    row["Pieces"],  # Now correctly computed
                    date,
                    store_name,
                )
            )
        connection.commit()
        cursor.close()
        connection.close()
        return {"message": "Indent uploaded successfully"}
    except Exception as e:
        return {"error": str(e)}


# View indent logic
def view_indent(date, store_name):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM indent WHERE date = %s AND store_name = %s"
        cursor.execute(query, (date, store_name))
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result
    except Exception as e:
        return {"error": str(e)}


# Edit indent logic
def edit_indent(product_number, bought_quantity, date, store_name):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
            UPDATE indent 
            SET bought_quantity = %s, date = %s, store_name = %s 
            WHERE product_number = %s
        """
        cursor.execute(query, (bought_quantity, date, store_name, product_number))
        connection.commit()
        cursor.close()
        connection.close()

        if cursor.rowcount == 0:
            return {"error": "No indent found with the given product number."}
        return {"message": "Indent updated successfully"}
    except Exception as e:
        return {"error": str(e)}


# Delete indent logic
def delete_indent(product_number, date, store_name):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "DELETE FROM indent WHERE product_number = %s AND date = %s AND store_name = %s"
        cursor.execute(query, (product_number, date, store_name))
        connection.commit()
        cursor.close()
        connection.close()

        if cursor.rowcount == 0:
            return {"error": "No indent found to delete."}
        return {"message": "Indent deleted successfully"}
    except Exception as e:
        return {"error": str(e)}