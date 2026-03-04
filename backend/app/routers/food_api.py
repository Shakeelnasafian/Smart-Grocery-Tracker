from fastapi import APIRouter, HTTPException, Query, Depends
import httpx
from app import schemas
from app.routers.auth import get_current_user

router = APIRouter(prefix="/food", tags=["Food Database"])

OPENFOODFACTS_URL = "https://world.openfoodfacts.org/cgi/search.pl"


@router.get("/search", response_model=list[schemas.FoodProductInfo])
async def search_food(
    q: str = Query(..., description="Product name to search"),
    _=Depends(get_current_user),
):
    """Search the Open Food Facts database for product information."""
    params = {
        "search_terms": q,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 5,
        "fields": "product_name,categories_tags,quantity,image_url,nutrition_grades,brands",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(OPENFOODFACTS_URL, params=params)
            response.raise_for_status()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Could not reach Open Food Facts API")

    data = response.json()
    products = data.get("products", [])

    results = []
    for p in products:
        name = p.get("product_name", "").strip()
        if not name:
            continue
        categories = p.get("categories_tags", [])
        category = categories[0].replace("en:", "").replace("-", " ").title() if categories else None
        results.append(
            schemas.FoodProductInfo(
                name=name,
                category=category,
                quantity=p.get("quantity"),
                image_url=p.get("image_url"),
                nutriscore=p.get("nutrition_grades"),
                brands=p.get("brands"),
            )
        )
    return results


@router.get("/barcode/{barcode}", response_model=schemas.FoodProductInfo)
async def get_by_barcode(barcode: str, _=Depends(get_current_user)):
    """Look up a product by its barcode via Open Food Facts."""
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Could not reach Open Food Facts API")

    data = response.json()
    if data.get("status") != 1:
        raise HTTPException(status_code=404, detail="Product not found")

    p = data["product"]
    categories = p.get("categories_tags", [])
    category = categories[0].replace("en:", "").replace("-", " ").title() if categories else None

    return schemas.FoodProductInfo(
        name=p.get("product_name", "Unknown"),
        category=category,
        quantity=p.get("quantity"),
        image_url=p.get("image_url"),
        nutriscore=p.get("nutrition_grades"),
        brands=p.get("brands"),
    )
