from fastapi import APIRouter
from backend.app.engines.product_engine import run_product_engine

router = APIRouter()

@router.post("/api/product/generate")
def generate_product_route():
    return run_product_engine()

