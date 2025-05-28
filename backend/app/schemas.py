from pydantic import BaseModel
from datetime import date
from typing import Optional

class GroceryItemBase(BaseModel):
    name: str
    quantity: str
    category: str
    expiry_date: date

class GroceryItemCreate(GroceryItemBase):
    pass

class GroceryItem(GroceryItemBase):
    id: int
    class Config:
        orm_mode = True
