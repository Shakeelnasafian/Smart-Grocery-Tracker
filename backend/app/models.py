from sqlalchemy import Column, Integer, String, Date, Float, Boolean, ForeignKey, DateTime, Text
from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    grocery_items = relationship("GroceryItem", back_populates="owner", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="owner", cascade="all, delete-orphan")
    shopping_items = relationship("ShoppingItem", back_populates="owner", cascade="all, delete-orphan")
    alert_settings = relationship("AlertSetting", back_populates="owner", uselist=False, cascade="all, delete-orphan")


class GroceryItem(Base):
    __tablename__ = "grocery_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(String)
    category = Column(String, index=True)
    expiry_date = Column(Date)
    price = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    is_consumed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="grocery_items")


class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer)   # 1-12
    year = Column(Integer)
    limit_amount = Column(Float)
    spent_amount = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="budgets")


class ShoppingItem(Base):
    __tablename__ = "shopping_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(String)
    category = Column(String)
    is_purchased = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="shopping_items")


class AlertSetting(Base):
    __tablename__ = "alert_settings"
    id = Column(Integer, primary_key=True, index=True)
    enabled = Column(Boolean, default=True)
    days_before_expiry = Column(Integer, default=3)
    email = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    owner = relationship("User", back_populates="alert_settings")
