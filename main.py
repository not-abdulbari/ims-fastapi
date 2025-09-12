from fastapi import FastAPI
from dotenv import load_dotenv
import os
from controllers.indent_controller import router as indent_router

# Load environment variables
load_dotenv()

app = FastAPI()

# Register the indent controller routes
app.include_router(indent_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Inventory Management System Backend is running"}
