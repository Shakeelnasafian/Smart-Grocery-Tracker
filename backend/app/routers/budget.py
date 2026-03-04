from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas, database
from app.routers.auth import get_current_user

router = APIRouter(prefix="/budget", tags=["Budget"])


@router.post("/", response_model=schemas.Budget, status_code=201)
def create_budget(
    budget: schemas.BudgetCreate,
    db: Session = Depends(database.get_db),
    user=Depends(get_current_user),
):
    existing = crud.get_budget(db, user.id, budget.month, budget.year)
    if existing:
        raise HTTPException(status_code=400, detail="Budget for this month/year already exists. Use PUT to update.")
    return crud.create_budget(db, budget, user.id)


@router.get("/", response_model=List[schemas.Budget])
def get_budgets(db: Session = Depends(database.get_db), user=Depends(get_current_user)):
    return crud.get_budgets(db, user.id)


@router.get("/{budget_id}", response_model=schemas.Budget)
def get_budget(budget_id: int, db: Session = Depends(database.get_db), user=Depends(get_current_user)):
    budgets = crud.get_budgets(db, user.id)
    budget = next((b for b in budgets if b.id == budget_id), None)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@router.put("/{budget_id}", response_model=schemas.Budget)
def update_budget(
    budget_id: int,
    updates: schemas.BudgetUpdate,
    db: Session = Depends(database.get_db),
    user=Depends(get_current_user),
):
    updated = crud.update_budget(db, budget_id, user.id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Budget not found")
    return updated
