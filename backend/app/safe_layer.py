from fastapi import APIRouter
import traceback, os, json

# === GLOBAL SAFE EXECUTION ===
def safe_execute(func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        return {"status": "success", "result": result}
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "trace": traceback.format_exc()
        }

# === FALLBACK FILE CREATOR ===
FALLBACK_PATH = "backend/outputs/fallback.txt"

def ensure_fallback():
    os.makedirs("backend/outputs", exist_ok=True)
    if not os.path.exists(FALLBACK_PATH):
        with open(FALLBACK_PATH, "w", encoding="utf-8") as f:
            f.write("Fallback output generated. System recovered safely.")
    return "/api/file/fallback.txt"

# === SAFE PRODUCT ROUTE ===
router = APIRouter()

@router.post("/safe-product-pack")
def safe_product_pack(payload: dict):
    from backend.app.main import generate_product_pack

    res = safe_execute(generate_product_pack, payload)

    if res["status"] == "error":
        return {
            "status": "fallback",
            "file_url": ensure_fallback(),
            "error": res["error"]
        }

    # guarantee file_url exists
    result = res.get("result", {})
    file_url = result.get("file_url") if isinstance(result, dict) else None

    if not file_url:
        file_url = ensure_fallback()

    return {
        "status": "success",
        "file_url": file_url,
        "data": result
    }
