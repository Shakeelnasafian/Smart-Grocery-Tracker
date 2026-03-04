from sqlalchemy import (
    Column, Integer, String, Date, Numeric, Boolean,
    ForeignKey, DateTime, Text, UniqueConstraint,
)
from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    grocery_items = relationship("GroceryItem", back_populates="owner", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="owner", cascade="all, delete-orphan")
    shopping_items = relationship("ShoppingItem", back_populates="owner", cascade="all, delete-orphan")
    alert_settings = relationship(
        "AlertSetting", back_populates="owner", uselist=False, cascade="all, delete-orphan"
    )


class GroceryItem(Base):
    __tablename__ = "grocery_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    quantity = Column(String, nullable=False)
    category = Column(String, index=True, nullable=False)
    expiry_date = Column(Date, nullable=False)
    # Numeric(10, 2) avoids float binary rounding drift in price calculations
    price = Column(Numeric(10, 2), nullable=True)
    notes = Column(Text, nullable=True)
    is_consumed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="grocery_items")


class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (UniqueConstraint("user_id", "month", "year", name="uq_budget_user_month_year"),)

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer, nullable=False)   # 1-12
    year = Column(Integer, nullable=False)
    limit_amount = Column(Numeric(10, 2), nullable=False)
    spent_amount = Column(Numeric(10, 2), default=0, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="budgets")


class ShoppingItem(Base):
    __tablename__ = "shopping_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    quantity = Column(String, nullable=False)
    category = Column(String, nullable=False)
    is_purchased = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="shopping_items")


class AlertSetting(Base):
    __tablename__ = "alert_settings"
    id = Column(Integer, primary_key=True, index=True)
    enabled = Column(Boolean, default=True, nullable=False)
    days_before_expiry = Column(Integer, default=3, nullable=False)
    email = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    owner = relationship("User", back_populates="alert_settings")
