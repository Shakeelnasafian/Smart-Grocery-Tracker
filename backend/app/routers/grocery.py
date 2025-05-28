from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, schemas, database
from app.routers import auth


router = APIRouter(prefix="/grocery", tags=["Grocery"])

@router.post("/", response_model=schemas.GroceryItem)
def create_item(item: schemas.GroceryItemCreate, db: Session = Depends(database.get_db), user=Depends(auth.get_current_user)):
    return crud.create_grocery_item(db, item, user.id)

@router.get("/", response_model=list[schemas.GroceryItem])
def get_items(db: Session = Depends(database.get_db), user=Depends(auth.get_current_user)):
    return crud.get_grocery_items(db, user.id)

@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(database.get_db), user=Depends(auth.get_current_user)):
    deleted = crud.delete_grocery_item(db, item_id, user.id)
    if not deleted:
        return {"detail": "Item not found"}
    return {"detail": "Deleted"}
