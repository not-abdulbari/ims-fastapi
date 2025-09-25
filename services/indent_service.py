from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
import pandas as pd
import io
import re

# We will use our SQLAlchemy model now
import models

# Helper function to extract weight and pieces details
# This function is excellent and has been kept as is.
def extract_details(product_name, requested_quantity):
    min_weight, max_weight, unit, pieces = None, None, None, None
    product_name_lower = product_name.lower()
    # ... (Your entire regex logic remains here, unchanged) ...
    # Pattern 1: (X - Y gm/kg)
    bracket_range = re.search(r"\(\s*([\d.]+)\s*-\s*([\d.]+)\s*(?:gm|g|kg)\s*\)", product_name_lower)
    # Pattern 2: X gm - Y gm
    dual_unit_range = re.search(r"([\d.]+)\s*(gm|g|kg)\s*-\s*([\d.]+)\s*(?:gm|g|kg)", product_name_lower)
    # Pattern 3: X - Y gm
    simple_range = re.search(r"([\d.]+)\s*-\s*([\d.]+)\s*(gm|g|kg)", product_name_lower)
    # Pattern 3.1: (X - Y) gm/kg
    bracketed_range_with_unit_after = re.search(r"\(\s*([\d.]+)\s*-\s*([\d.]+)\s*\)\s*(gm|g|kg)", product_name_lower)
    # Pattern 4: Single weight
    single_value = re.search(r"([\d.]+)\s*(gm|g|kg)", product_name_lower)
    # Pattern 5: Numeric Units
    num_units = re.search(r"(\d+)\s*(units?|pieces?)", product_name_lower)

    if bracket_range:
        min_val, max_val, unit = float(bracket_range.group(1)), float(bracket_range.group(2)), "g"
        min_weight, max_weight = min_val * requested_quantity, max_val * requested_quantity
    elif dual_unit_range:
        min_val, max_val, unit = float(dual_unit_range.group(1)), float(dual_unit_range.group(3)), dual_unit_range.group(2)
        min_weight, max_weight = min_val * requested_quantity, max_val * requested_quantity
    elif simple_range:
        min_val, max_val, unit = float(simple_range.group(1)), float(simple_range.group(2)), simple_range.group(3)
        min_weight, max_weight = min_val * requested_quantity, max_val * requested_quantity
    elif bracketed_range_with_unit_after:
        min_val, max_val, unit = float(bracketed_range_with_unit_after.group(1)), float(bracketed_range_with_unit_after.group(2)), bracketed_range_with_unit_after.group(3)
        min_weight, max_weight = min_val * requested_quantity, max_val * requested_quantity
    elif single_value:
        min_weight, max_weight, unit = float(single_value.group(1)) * requested_quantity, None, single_value.group(2)
    elif num_units:
        pieces, unit = int(num_units.group(1)) * requested_quantity, "Unit"
    elif "unit" in product_name_lower or "piece" in product_name_lower:
        unit = "Unit"
    
    if unit in ["gm", "g"]: unit = "g"
    return min_weight, max_weight, unit, pieces

# --- REFACTORED DATABASE LOGIC ---

# Note how each function now accepts `db: Session`
def upload_indent(db: Session, file: UploadFile, date: str, store_name: str):
    try:
        content = file.file.read()
        df = pd.read_excel(io.BytesIO(content))

        required_columns = {"Product Number", "Product Name", "Requested Quantity"}
        if not required_columns.issubset(df.columns):
            raise HTTPException(status_code=400, detail=f"Missing required columns: {required_columns}")

        for _, row in df.iterrows():
            min_w, max_w, u, p = extract_details(row["Product Name"], row["Requested Quantity"])
            
            # Create a new Indent object using our SQLAlchemy model
            new_indent_item = models.Indent(
                product_number=row["Product Number"],
                product_name=row["Product Name"],
                requested_quantity=row["Requested Quantity"],
                min_weight=min_w,
                max_weight=max_w,
                unit=u,
                pieces=p,
                date=date,
                store_name=store_name
            )
            db.add(new_indent_item) # Add the object to the session

        db.commit() # Commit all new items to the database in one transaction
        return {"message": "Indent uploaded successfully"}
    except Exception as e:
        db.rollback() # If anything fails, undo the changes
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def view_indent(db: Session, date: str, store_name: str):
    # Use the ORM to build a query safely
    results = db.query(models.Indent).filter(
        models.Indent.date == date,
        models.Indent.store_name == store_name
    ).all()
    return results

def edit_indent(db: Session, product_number: str, bought_quantity: int, date: str, store_name: str):
    # First, find the record to update
    indent_item = db.query(models.Indent).filter(
        models.Indent.product_number == product_number,
        models.Indent.date == date,
        models.Indent.store_name == store_name
    ).first()

    if not indent_item:
        raise HTTPException(status_code=404, detail="Indent item not found.")

    # Update the field and commit
    indent_item.bought_quantity = bought_quantity
    db.commit()
    db.refresh(indent_item) # Refresh the object with data from the DB
    return {"message": "Indent updated successfully", "data": indent_item}

def delete_indent(db: Session, product_number: str, date: str, store_name: str):
    # Find the record to delete
    indent_item = db.query(models.Indent).filter(
        models.Indent.product_number == product_number,
        models.Indent.date == date,
        models.Indent.store_name == store_name
    ).first()

    if not indent_item:
        raise HTTPException(status_code=404, detail="Indent item not found to delete.")

    # Delete the record and commit
    db.delete(indent_item)
    db.commit()
    return {"message": "Indent deleted successfully"}