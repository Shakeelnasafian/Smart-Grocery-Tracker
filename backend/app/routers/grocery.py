from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from app import crud, schemas, database
from app.routers.auth import get_current_user
import csv
import io
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/grocery", tags=["Grocery"])


@router.post("/", response_model=schemas.GroceryItem, status_code=201)
def create_item(
    item: schemas.GroceryItemCreate,
    db: Session = Depends(database.get_db),
    user=Depends(get_current_user),
):
    return crud.create_grocery_item(db, item, user.id)


@router.get("/", response_model=schemas.GroceryItemPage)
def get_items(
    search: Optional[str] = Query(None, description="Search by item name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    expiring_within_days: Optional[int] = Query(None, description="Items expiring within N days"),
    show_consumed: bool = Query(False, description="Include consumed items"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(database.get_db),
    user=Depends(get_current_user),
):
    return crud.get_grocery_items(
        db,
        user.id,
        search=search,
        category=category,
        expiring_within_days=expiring_within_days,
        show_consumed=show_consumed,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=schemas.GroceryItem)
def get_item(item_id: int, db: Session = Depends(database.get_db), user=Depends(get_current_user)):
    item = crud.get_grocery_item(db, item_id, user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=schemas.GroceryItem)
def update_item(
    item_id: int,
    updates: schemas.GroceryItemUpdate,
    db: Session = Depends(database.get_db),
    user=Depends(get_current_user),
):
    item = crud.update_grocery_item(db, item_id, user.id, updates)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(database.get_db), user=Depends(get_current_user)):
    deleted = crud.delete_grocery_item(db, item_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"detail": "Item deleted successfully"}


@router.get("/export/csv")
def export_csv(db: Session = Depends(database.get_db), user=Depends(get_current_user)):
    # Fetch all items without a page_size cap to avoid silent truncation
    items = crud.get_all_grocery_items(db, user.id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["ID", "Name", "Quantity", "Category", "Expiry Date", "Price", "Notes", "Consumed", "Created At"]
    )
    for item in items:
        writer.writerow([
            item.id,
            item.name,
            item.quantity,
            item.category,
            item.expiry_date,
            float(item.price) if item.price is not None else "",
            item.notes or "",
            item.is_consumed,
            item.created_at.strftime("%Y-%m-%d %H:%M") if item.created_at else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=grocery_list.csv"},
    )
