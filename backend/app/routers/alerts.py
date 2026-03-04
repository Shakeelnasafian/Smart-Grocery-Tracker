from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud, schemas, database
from app.routers.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/settings", response_model=schemas.AlertSettingOut)
def get_alert_settings(db: Session = Depends(database.get_db), user=Depends(get_current_user)):
    setting = crud.get_alert_setting(db, user.id)
    if not setting:
        raise HTTPException(status_code=404, detail="No alert settings found. Create one first.")
    return setting


@router.post("/settings", response_model=schemas.AlertSettingOut)
def upsert_alert_settings(
    data: schemas.AlertSettingCreate,
    db: Session = Depends(database.get_db),
    user=Depends(get_current_user),
):
    return crud.upsert_alert_setting(db, user.id, data)


@router.get("/expiring")
def get_expiring_items(
    days: int = Query(3, ge=1, le=365, description="Items expiring within N days (1–365)"),
    db: Session = Depends(database.get_db),
    user=Depends(get_current_user),
):
    """Returns grocery items expiring within N days."""
    items = crud.get_expiring_items(db, user.id, days=days)
    return {
        "expiring_within_days": days,
        "count": len(items),
        "items": [
            {
                "id": i.id,
                "name": i.name,
                "category": i.category,
                "expiry_date": str(i.expiry_date),
                "quantity": i.quantity,
            }
            for i in items
        ],
    }
