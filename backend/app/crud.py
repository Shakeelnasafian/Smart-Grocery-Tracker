from sqlalchemy.orm import Session
from app import models, schemas
from datetime import date

def create_grocery_item(db: Session, item: schemas.GroceryItemCreate, user_id: int):
    db_item = models.GroceryItem(**item.dict(), user_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_grocery_items(db: Session, user_id: int):
    return db.query(models.GroceryItem).filter(models.GroceryItem.user_id == user_id).all()

def delete_grocery_item(db: Session, item_id: int, user_id: int):
    item = db.query(models.GroceryItem).filter_by(id=item_id, user_id=user_id).first()
    if item:
        db.delete(item)
        db.commit()
    return item

def get_grocery_item(db: Session, item_id: int, user_id: int):
    return db.query(models.GroceryItem).filter_by(id=item_id, user_id=user_id).first()
