from fastapi import APIRouter, UploadFile, File
from services.indent_service import upload_indent, view_indent, edit_indent, delete_indent

router = APIRouter(prefix="/indent", tags=["indent-controller"])

# Define routes for indent services
@router.post("/upload")
def upload_indent_endpoint(date: str, store_name: str, file: UploadFile = File(...)):
    return upload_indent(file, date, store_name)

@router.get("/view")
def view_indent_endpoint(date: str, store_name: str):
    return view_indent(date, store_name)

@router.put("/edit")
def edit_indent_endpoint(product_number: int, bought_quantity: int, date: str, store_name: str):
    return edit_indent(product_number, bought_quantity, date, store_name)

@router.delete("/delete")
def delete_indent_endpoint(product_number: int, date: str, store_name: str):
    return delete_indent(product_number, date, store_name)
