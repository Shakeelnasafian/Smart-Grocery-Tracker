from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, database, schemas
from app.routers.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/", response_model=schemas.AnalyticsSummary)
def get_analytics(db: Session = Depends(database.get_db), user=Depends(get_current_user)):
    return crud.get_analytics(db, user.id)
