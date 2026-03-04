from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas, database
from app.routers.auth import get_current_user

router = APIRouter(prefix="/shopping", tags=["Shopping List"])


@router.get("/", response_model=List[schemas.ShoppingItem])
def get_shopping_items(db: Session = Depends(database.get_db), user=Depends(get_current_user)):
    return crud.get_shopping_items(db, user.id)


@router.post("/", response_model=schemas.ShoppingItem, status_code=201)
def add_shopping_item(
    item: schemas.ShoppingItemCreate,
    db: Session = Depends(database.get_db),
    user=Depends(get_current_user),
):
    return crud.create_shopping_item(db, item, user.id)


@router.put("/{item_id}", response_model=schemas.ShoppingItem)
def update_shopping_item(
    item_id: int,
    updates: schemas.ShoppingItemUpdate,
    db: Session = Depends(database.get_db),
    user=Depends(get_current_user),
):
    item = crud.update_shopping_item(db, item_id, user.id, updates)
    if not item:
        raise HTTPException(status_code=404, detail="Shopping item not found")
    return item


@router.delete("/{item_id}")
def delete_shopping_item(
    item_id: int,
    db: Session = Depends(database.get_db),
    user=Depends(get_current_user),
):
    deleted = crud.delete_shopping_item(db, item_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Shopping item not found")
    return {"detail": "Shopping item deleted"}


@router.post("/generate", response_model=List[schemas.ShoppingItem])
def generate_shopping_list(db: Session = Depends(database.get_db), user=Depends(get_current_user)):
    """Auto-generate shopping list from expired/consumed grocery items."""
    added = crud.generate_shopping_list(db, user.id)
    return added
