from sqlalchemy import Column, Integer, String, Date
from database import Base

class Indent(Base):
    # This must match your SQL table name exactly
    __tablename__ = "indent"

    id = Column(Integer, primary_key=True) # SQLAlchemy handles AUTO_INCREMENT
    product_number = Column(String(50))
    product_name = Column(String(255))
    requested_quantity = Column(Integer)
    pieces = Column(Integer)
    date = Column(Date) # Using the proper Date type
    store_name = Column(String(255))
    bought_quantity = Column(Integer)
    min_weight = Column(Integer)
    max_weight = Column(Integer)
    unit = Column(String(50))