from fastapi import APIRouter, HTTPException
import importlib

router = APIRouter()

@router.post("/run")
async def run_system(payload: dict):
    engine_name = payload.get("engine")
    data = payload.get("payload", {})

    if not engine_name:
        raise HTTPException(status_code=400, detail="No engine provided")

    try:
        module = importlib.import_module(f"backend.app.engines.{engine_name}")
        result = module.run(data)

        return {
            "engine": engine_name,
            "input": data,
            "result": result
        }

    except Exception as e:
        return {
            "engine": engine_name,
            "error": str(e)
        }
