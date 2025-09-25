from dotenv import load_dotenv

load_dotenv()


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from controllers.indent_controller import router as indent_router
import models
from database import engine

# This line tells SQLAlchemy to create all tables if they don't already exist.
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the indent controller routes
app.include_router(indent_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Inventory Management System Backend is running"}