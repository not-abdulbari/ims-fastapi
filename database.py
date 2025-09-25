import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. Get the Database URL from environment variables
#    FORMAT: mysql+pymysql://USER:PASSWORD@HOST/DATABASE_NAME
DATABASE_URL = os.getenv("DATABASE_URL")

# Check if the database URL is set
if not DATABASE_URL:
    raise ValueError("No DATABASE_URL environment variable set!")

# 2. Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# 3. Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create a Base class for your models to inherit from
Base = declarative_base()

# 5. Dependency to get a DB session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()