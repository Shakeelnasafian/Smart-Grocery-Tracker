from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from datetime import datetime
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


class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)