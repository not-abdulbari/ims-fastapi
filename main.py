from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
from controllers.indent_controller import router as indent_router

# Load environment variables
load_dotenv()

app = FastAPI()
# Add CORS middleware - place this right after creating the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Access-Control-Allow-Origin"]
)



# Register the indent controller routes
app.include_router(indent_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Inventory Management System Backend is running"}
