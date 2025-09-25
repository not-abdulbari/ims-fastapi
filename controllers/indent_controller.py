from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

# Import the service module and the get_db dependency
from services import indent_service
from database import get_db

router = APIRouter(prefix="/indent", tags=["indent-controller"])

# Define routes for indent services
@router.post("/upload")
def upload_indent_endpoint(
    date: str,
    store_name: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db) # <-- Add dependency
):
    # Pass the db session to the service function
    return indent_service.upload_indent(db=db, file=file, date=date, store_name=store_name)

@router.get("/view")
def view_indent_endpoint(date: str, store_name: str, db: Session = Depends(get_db)): # <-- Add dependency
    return indent_service.view_indent(db=db, date=date, store_name=store_name)

@router.put("/edit")
def edit_indent_endpoint(
    # The product_number in your table is a string (VARCHAR), not an integer
    product_number: str,
    bought_quantity: int,
    date: str,
    store_name: str,
    db: Session = Depends(get_db) # <-- Add dependency
):
    return indent_service.edit_indent(
        db=db,
        product_number=product_number,
        bought_quantity=bought_quantity,
        date=date,
        store_name=store_name
    )

@router.delete("/delete")
def delete_indent_endpoint(
    product_number: str, # <-- Corrected type to string
    date: str,
    store_name: str,
    db: Session = Depends(get_db) # <-- Add dependency
):
    return indent_service.delete_indent(
        db=db,
        product_number=product_number,
        date=date,
        store_name=store_name
    )