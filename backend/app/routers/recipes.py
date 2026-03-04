from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import httpx
from app import database, crud
from app.routers.auth import get_current_user
from app.config import settings
from datetime import date

router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.get("/suggestions")
async def get_recipe_suggestions(
    db: Session = Depends(database.get_db),
    user=Depends(get_current_user),
):
    """Suggest recipes based on current grocery inventory using Spoonacular API."""
    result = crud.get_grocery_items(db, user.id, page_size=50)
    ingredients = [item.name for item in result["items"]]

    if not ingredients:
        return {"recipes": [], "message": "No grocery items found to suggest recipes from."}

    if not settings.SPOONACULAR_API_KEY:
        # Return mock suggestions if no API key configured
        return {
            "recipes": [
                {
                    "title": "Sample Recipe",
                    "readyInMinutes": 30,
                    "servings": 4,
                    "sourceUrl": "#",
                    "image": None,
                    "usedIngredients": ingredients[:3],
                    "missedIngredients": [],
                }
            ],
            "message": "Configure SPOONACULAR_API_KEY in .env for real recipe suggestions.",
        }

    ingredients_str = ",".join(ingredients[:10])
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "ingredients": ingredients_str,
        "number": 5,
        "ranking": 1,
        "ignorePantry": True,
        "apiKey": settings.SPOONACULAR_API_KEY,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Could not reach Spoonacular API")

    recipes = response.json()
    return {
        "recipes": [
            {
                "id": r.get("id"),
                "title": r.get("title"),
                "image": r.get("image"),
                "usedIngredients": [i["name"] for i in r.get("usedIngredients", [])],
                "missedIngredients": [i["name"] for i in r.get("missedIngredients", [])],
                "likes": r.get("likes", 0),
            }
            for r in recipes
        ]
    }
