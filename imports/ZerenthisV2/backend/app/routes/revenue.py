from fastapi import APIRouter
from backend.app.routes.full_cycle import full_cycle
from backend.app.engines.store_engine import build_store
from backend.app.engines.traffic_engine import run_traffic_engine
from backend.app.engines.conversion_engine import run_conversion_engine
from backend.app.engines.leaderboard_engine import update_leaderboard

router = APIRouter()

@router.post("/api/revenue/run")
def revenue_loop():
    cycle = full_cycle()

    product = cycle["product"]["product"]

    store = build_store(product)

    traffic = run_traffic_engine()
    conv = run_conversion_engine(traffic["visitors"])

    leaderboard = update_leaderboard(conv["revenue"], conv["conversions"])

    return {
        "status": "revenue_loop_complete",
        "cycle": cycle,
        "traffic": traffic,
        "conversion": conv,
        "leaderboard": leaderboard
    }
