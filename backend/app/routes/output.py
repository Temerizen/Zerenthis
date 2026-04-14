from fastapi import APIRouter
from backend.app.engines.output_engine import generate_best_output

router = APIRouter()

@router.post("/output/generate")
def generate_output():
    return generate_best_output()


