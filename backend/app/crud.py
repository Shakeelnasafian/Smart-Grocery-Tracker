from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app import models, schemas
from datetime import date, timedelta
from typing import Optional, List
import math


# ── Grocery Items ─────────────────────────────────────────────────────────────

def create_grocery_item(db: Session, item: schemas.GroceryItemCreate, user_id: int):
    db_item = models.GroceryItem(**item.dict(), user_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    _sync_budget_spending(db, user_id)
    return db_item


def get_grocery_items(
    db: Session,
    user_id: int,
    search: Optional[str] = None,
    category: Optional[str] = None,
    expiring_within_days: Optional[int] = None,
    show_consumed: bool = False,
    page: int = 1,
    page_size: int = 20,
):
    query = db.query(models.GroceryItem).filter(models.GroceryItem.user_id == user_id)

    if not show_consumed:
        query = query.filter(models.GroceryItem.is_consumed == False)

    if search:
        query = query.filter(models.GroceryItem.name.ilike(f"%{search}%"))

    if category:
        query = query.filter(models.GroceryItem.category.ilike(f"%{category}%"))

    if expiring_within_days is not None:
        threshold = date.today() + timedelta(days=expiring_within_days)
        query = query.filter(
            models.GroceryItem.expiry_date <= threshold,
            models.GroceryItem.expiry_date >= date.today(),
        )

    total = query.count()
    items = query.order_by(models.GroceryItem.expiry_date.asc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if total else 1,
    }


def get_grocery_item(db: Session, item_id: int, user_id: int):
    return db.query(models.GroceryItem).filter_by(id=item_id, user_id=user_id).first()


def update_grocery_item(db: Session, item_id: int, user_id: int, updates: schemas.GroceryItemUpdate):
    item = get_grocery_item(db, item_id, user_id)
    if not item:
        return None
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    _sync_budget_spending(db, user_id)
    return item


def delete_grocery_item(db: Session, item_id: int, user_id: int):
    item = get_grocery_item(db, item_id, user_id)
    if item:
        db.delete(item)
        db.commit()
        _sync_budget_spending(db, user_id)
    return item


def get_expiring_items(db: Session, user_id: int, days: int = 3) -> List[models.GroceryItem]:
    threshold = date.today() + timedelta(days=days)
    return (
        db.query(models.GroceryItem)
        .filter(
            models.GroceryItem.user_id == user_id,
            models.GroceryItem.expiry_date <= threshold,
            models.GroceryItem.expiry_date >= date.today(),
            models.GroceryItem.is_consumed == False,
        )
        .all()
    )


# ── Budget ────────────────────────────────────────────────────────────────────

def create_budget(db: Session, budget: schemas.BudgetCreate, user_id: int):
    db_budget = models.Budget(**budget.dict(), user_id=user_id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


def get_budget(db: Session, user_id: int, month: int, year: int):
    return db.query(models.Budget).filter_by(user_id=user_id, month=month, year=year).first()


def get_budgets(db: Session, user_id: int):
    return db.query(models.Budget).filter_by(user_id=user_id).order_by(models.Budget.year.desc(), models.Budget.month.desc()).all()


def update_budget(db: Session, budget_id: int, user_id: int, updates: schemas.BudgetUpdate):
    budget = db.query(models.Budget).filter_by(id=budget_id, user_id=user_id).first()
    if not budget:
        return None
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(budget, field, value)
    db.commit()
    db.refresh(budget)
    return budget


def _sync_budget_spending(db: Session, user_id: int):
    """Recalculate current month's budget spent from grocery items with prices."""
    today = date.today()
    budget = get_budget(db, user_id, today.month, today.year)
    if not budget:
        return
    total = (
        db.query(func.sum(models.GroceryItem.price))
        .filter(
            models.GroceryItem.user_id == user_id,
            extract("month", models.GroceryItem.created_at) == today.month,
            extract("year", models.GroceryItem.created_at) == today.year,
            models.GroceryItem.price.isnot(None),
        )
        .scalar()
    ) or 0.0
    budget.spent_amount = total
    db.commit()


# ── Shopping List ─────────────────────────────────────────────────────────────

def get_shopping_items(db: Session, user_id: int):
    return db.query(models.ShoppingItem).filter_by(user_id=user_id).order_by(models.ShoppingItem.is_purchased).all()


def create_shopping_item(db: Session, item: schemas.ShoppingItemCreate, user_id: int):
    db_item = models.ShoppingItem(**item.dict(), user_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_shopping_item(db: Session, item_id: int, user_id: int, updates: schemas.ShoppingItemUpdate):
    item = db.query(models.ShoppingItem).filter_by(id=item_id, user_id=user_id).first()
    if not item:
        return None
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def delete_shopping_item(db: Session, item_id: int, user_id: int):
    item = db.query(models.ShoppingItem).filter_by(id=item_id, user_id=user_id).first()
    if item:
        db.delete(item)
        db.commit()
    return item


def generate_shopping_list(db: Session, user_id: int):
    """Auto-generate shopping list from expired + consumed grocery items."""
    expired_or_consumed = (
        db.query(models.GroceryItem)
        .filter(
            models.GroceryItem.user_id == user_id,
            (models.GroceryItem.expiry_date < date.today()) | (models.GroceryItem.is_consumed == True),
        )
        .all()
    )
    added = []
    for item in expired_or_consumed:
        exists = db.query(models.ShoppingItem).filter_by(user_id=user_id, name=item.name, is_purchased=False).first()
        if not exists:
            new_item = models.ShoppingItem(
                name=item.name,
                quantity=item.quantity,
                category=item.category,
                user_id=user_id,
                notes="Auto-generated from inventory",
            )
            db.add(new_item)
            added.append(new_item)
    db.commit()
    return added


# ── Analytics ─────────────────────────────────────────────────────────────────

def get_analytics(db: Session, user_id: int) -> dict:
    today = date.today()

    all_items = db.query(models.GroceryItem).filter_by(user_id=user_id).all()
    total_items = len(all_items)
    consumed_items = sum(1 for i in all_items if i.is_consumed)
    total_spent = sum(i.price for i in all_items if i.price) or 0.0
    waste_rate = round((consumed_items / total_items * 100) if total_items else 0, 1)

    expired = sum(1 for i in all_items if not i.is_consumed and i.expiry_date and i.expiry_date < today)
    expiring_soon = sum(
        1 for i in all_items
        if not i.is_consumed and i.expiry_date and today <= i.expiry_date <= today + timedelta(days=3)
    )
    fresh = total_items - consumed_items - expired - expiring_soon

    # Category breakdown
    category_map: dict = {}
    for item in all_items:
        cat = item.category or "Uncategorized"
        if cat not in category_map:
            category_map[cat] = {"category": cat, "count": 0, "total_spent": 0.0}
        category_map[cat]["count"] += 1
        category_map[cat]["total_spent"] += item.price or 0.0

    # Monthly spending (last 6 months)
    monthly = (
        db.query(
            extract("year", models.GroceryItem.created_at).label("year"),
            extract("month", models.GroceryItem.created_at).label("month"),
            func.sum(models.GroceryItem.price).label("total"),
        )
        .filter(models.GroceryItem.user_id == user_id, models.GroceryItem.price.isnot(None))
        .group_by("year", "month")
        .order_by("year", "month")
        .limit(6)
        .all()
    )

    return {
        "total_items": total_items,
        "total_spent": round(total_spent, 2),
        "consumed_items": consumed_items,
        "waste_rate": waste_rate,
        "expiry_stats": {"expired": expired, "expiring_soon": expiring_soon, "fresh": max(fresh, 0)},
        "category_breakdown": list(category_map.values()),
        "monthly_spending": [
            {"year": int(m.year), "month": int(m.month), "total": round(m.total or 0, 2)}
            for m in monthly
        ],
    }


# ── Alert Settings ────────────────────────────────────────────────────────────

def get_alert_setting(db: Session, user_id: int):
    return db.query(models.AlertSetting).filter_by(user_id=user_id).first()


def upsert_alert_setting(db: Session, user_id: int, data: schemas.AlertSettingCreate):
    setting = get_alert_setting(db, user_id)
    if setting:
        setting.enabled = data.enabled
        setting.days_before_expiry = data.days_before_expiry
        setting.email = data.email
    else:
        setting = models.AlertSetting(**data.dict(), user_id=user_id)
        db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting
