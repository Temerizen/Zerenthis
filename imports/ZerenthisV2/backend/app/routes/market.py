from fastapi import APIRouter, Header, HTTPException
import traceback
from pydantic import BaseModel

from backend.app.engines.market_access_engine import is_founder
from backend.app.engines.market_portfolio_engine import load_portfolio
from backend.app.engines.market_state_engine import load_market_state
from backend.app.engines.market_strategy_leaderboard import load_strategy_board
from backend.app.engines.market_genetics_engine import load_genetics
from backend.app.engines.trade_memory import get_stats
from backend.app.engines.founder_market_canonical_engine import (
    reset_founder_portfolio,
    run_strategy_cycle,
    run_winner_cycle,
    run_full_cycle,
)

router = APIRouter()

class PortfolioResetRequest(BaseModel):
    starting_balance: float = 50.0
    risk_per_trade: float = 0.10

@router.post("/founder/market/reset-portfolio")
def founder_market_reset_portfolio(payload: PortfolioResetRequest, x_api_key: str = Header(None)):
    if not is_founder(x_api_key):
        raise HTTPException(status_code=401, detail="unauthorized")
    try:
        return reset_founder_portfolio(payload.starting_balance, payload.risk_per_trade)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"reset_portfolio_failed: {e}")

@router.post("/founder/market/run")
def founder_market_run(x_api_key: str = Header(None)):
    if not is_founder(x_api_key):
        raise HTTPException(status_code=401, detail="unauthorized")
    try:
        return run_full_cycle()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"founder_market_run_failed: {e}`nTRACEBACK:`n{traceback.format_exc()}")

@router.post("/founder/market/strategy-run")
def founder_market_strategy_run(x_api_key: str = Header(None)):
    if not is_founder(x_api_key):
        raise HTTPException(status_code=401, detail="unauthorized")
    try:
        return run_strategy_cycle()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"founder_market_strategy_run_failed: {e}")

@router.post("/founder/market/winner-run")
def founder_market_winner_run(x_api_key: str = Header(None)):
    if not is_founder(x_api_key):
        raise HTTPException(status_code=401, detail="unauthorized")
    try:
        return run_winner_cycle()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"founder_market_winner_run_failed: {e}")

@router.get("/market/portfolio")
def market_portfolio():
    return load_portfolio()

@router.get("/market/latest")
def market_latest():
    return load_market_state()

@router.get("/market/performance")
def market_performance():
    state = load_market_state()
    return {
        "score": state.get("score", {}),
        "performance": state.get("performance", {}),
        "portfolio": load_portfolio(),
        "best_strategy": state.get("best_strategy"),
        "updated_at": state.get("updated_at")
    }

@router.get("/market/strategy-board")
def market_strategy_board():
    return load_strategy_board()

@router.get("/market/genetics")
def market_genetics():
    return load_genetics()

@router.get("/market/stats")
def market_stats():
    return get_stats()

