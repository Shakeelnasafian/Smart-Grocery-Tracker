from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List


# ── Grocery ──────────────────────────────────────────────────────────────────

class GroceryItemBase(BaseModel):
    name: str
    quantity: str
    category: str
    expiry_date: date
    price: Optional[float] = None
    notes: Optional[str] = None


class GroceryItemCreate(GroceryItemBase):
    pass


class GroceryItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[str] = None
    category: Optional[str] = None
    expiry_date: Optional[date] = None
    price: Optional[float] = None
    notes: Optional[str] = None
    is_consumed: Optional[bool] = None


class GroceryItem(GroceryItemBase):
    id: int
    is_consumed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class GroceryItemPage(BaseModel):
    items: List[GroceryItem]
    total: int
    page: int
    page_size: int
    pages: int


# ── Auth ─────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# ── Budget ───────────────────────────────────────────────────────────────────

class BudgetCreate(BaseModel):
    month: int
    year: int
    limit_amount: float


class BudgetUpdate(BaseModel):
    limit_amount: Optional[float] = None
    spent_amount: Optional[float] = None


class Budget(BaseModel):
    id: int
    month: int
    year: int
    limit_amount: float
    spent_amount: float
    created_at: datetime

    class Config:
        from_attributes = True


# ── Shopping List ─────────────────────────────────────────────────────────────

class ShoppingItemCreate(BaseModel):
    name: str
    quantity: str
    category: str
    notes: Optional[str] = None


class ShoppingItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[str] = None
    category: Optional[str] = None
    is_purchased: Optional[bool] = None
    notes: Optional[str] = None


class ShoppingItem(BaseModel):
    id: int
    name: str
    quantity: str
    category: str
    is_purchased: bool
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Analytics ────────────────────────────────────────────────────────────────

class CategoryBreakdown(BaseModel):
    category: str
    count: int
    total_spent: float


class ExpiryStats(BaseModel):
    expired: int
    expiring_soon: int
    fresh: int


class AnalyticsSummary(BaseModel):
    total_items: int
    total_spent: float
    consumed_items: int
    waste_rate: float
    expiry_stats: ExpiryStats
    category_breakdown: List[CategoryBreakdown]
    monthly_spending: List[dict]


# ── Alert Settings ────────────────────────────────────────────────────────────

class AlertSettingCreate(BaseModel):
    enabled: bool = True
    days_before_expiry: int = 3
    email: str


class AlertSettingOut(BaseModel):
    id: int
    enabled: bool
    days_before_expiry: int
    email: str

    class Config:
        from_attributes = True


# ── Open Food Facts ───────────────────────────────────────────────────────────

class FoodProductInfo(BaseModel):
    name: str
    category: Optional[str] = None
    quantity: Optional[str] = None
    image_url: Optional[str] = None
    nutriscore: Optional[str] = None
    brands: Optional[str] = None
