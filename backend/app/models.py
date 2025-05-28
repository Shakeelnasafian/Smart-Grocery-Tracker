from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class GroceryItem(Base):
    __tablename__ = "grocery_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(String)
    category = Column(String)
    expiry_date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User")
