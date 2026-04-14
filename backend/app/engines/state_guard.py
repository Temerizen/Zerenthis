import json
from pathlib import Path
from typing import Any, Dict, List

def _utf8_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8-sig")
    except Exception:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""

def safe_load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        raw = _utf8_text(path).strip()
        if not raw:
            return default
        return json.loads(raw)
    except Exception:
        return default

def safe_save_json(path: Path, data: Any) -> Any:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data

def _as_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default

def _as_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return default

def _as_list(v: Any, default: List[Any] = None) -> List[Any]:
    if isinstance(v, list):
        return v
    return [] if default is None else default

def normalize_portfolio(raw: Dict[str, Any] | None) -> Dict[str, Any]:
    raw = raw or {}
    starting_balance = round(max(1.0, _as_float(raw.get("starting_balance", 50.0), 50.0)), 2)
    balance = round(_as_float(raw.get("balance", starting_balance), starting_balance), 2)
    risk_per_trade = round(min(max(_as_float(raw.get("risk_per_trade", 0.10), 0.10), 0.001), 1.0), 4)
    last_run_trades = _as_list(raw.get("last_run_trades", []), [])
    equity_curve = _as_list(raw.get("equity_curve", [starting_balance]), [starting_balance])
    if not equity_curve:
        equity_curve = [starting_balance]
    return {
        "starting_balance": starting_balance,
        "balance": balance,
        "risk_per_trade": risk_per_trade,
        "max_open_positions": max(1, _as_int(raw.get("max_open_positions", 3), 3)),
        "last_run_trades": last_run_trades,
        "equity_curve": equity_curve,
        "peak_balance": round(_as_float(raw.get("peak_balance", max(equity_curve + [balance])), max(equity_curve + [balance])), 2)
    }

def normalize_strategy_row(raw: Dict[str, Any] | None) -> Dict[str, Any]:
    raw = raw or {}
    return {
        "runs": _as_int(raw.get("runs", 0), 0),
        "total_profit": round(_as_float(raw.get("total_profit", 0.0), 0.0), 4),
        "total_trades": _as_int(raw.get("total_trades", 0), 0),
        "wins": _as_int(raw.get("wins", 0), 0),
        "losses": _as_int(raw.get("losses", 0), 0),
        "last_profit": round(_as_float(raw.get("last_profit", 0.0), 0.0), 4),
        "avg_profit": round(_as_float(raw.get("avg_profit", 0.0), 0.0), 4),
        "avg_winrate": round(_as_float(raw.get("avg_winrate", 0.0), 0.0), 2),
    }

def normalize_strategy_board(raw: Dict[str, Any] | None) -> Dict[str, Any]:
    raw = raw or {}
    strategies = {}
    for name, row in (raw.get("strategies", {}) or {}).items():
        strategies[str(name)] = normalize_strategy_row(row)
    return {
        "strategies": strategies,
        "last_best_strategy": raw.get("last_best_strategy")
    }

def normalize_memory(raw: Dict[str, Any] | None) -> Dict[str, Any]:
    raw = raw or {}
    assets = {}
    for name, row in (raw.get("assets", {}) or {}).items():
        row = row or {}
        assets[str(name)] = {
            "wins": _as_int(row.get("wins", 0), 0),
            "losses": _as_int(row.get("losses", 0), 0),
            "total_profit": round(_as_float(row.get("total_profit", 0.0), 0.0), 4),
        }
    return {
        "assets": assets,
        "total_runs": _as_int(raw.get("total_runs", 0), 0)
    }

def normalize_genetics(raw: Dict[str, Any] | None) -> Dict[str, Any]:
    defaults = {
        "momentum": {"threshold": 2.0, "confidence_mult": 1.5, "max_conf": 10.0},
        "mean_reversion": {"threshold": 3.0, "confidence_mult": 1.2, "max_conf": 10.0},
        "breakout": {"threshold": 5.0, "confidence_mult": 2.0, "max_conf": 10.0},
        "conservative": {"threshold": 4.0, "confidence_mult": 1.0, "max_conf": 6.0},
    }
    raw = raw or {}
    out = {}
    for name, base in defaults.items():
        row = raw.get(name, {}) or {}
        out[name] = {
            "threshold": round(_as_float(row.get("threshold", base["threshold"]), base["threshold"]), 4),
            "confidence_mult": round(_as_float(row.get("confidence_mult", base["confidence_mult"]), base["confidence_mult"]), 4),
            "max_conf": round(_as_float(row.get("max_conf", base["max_conf"]), base["max_conf"]), 4),
        }
    return out

def normalize_performance(raw: Dict[str, Any] | None) -> Dict[str, Any]:
    raw = raw or {}
    equity_curve = _as_list(raw.get("equity_curve", []), [])
    return {
        "equity_curve": equity_curve,
        "max_drawdown": round(_as_float(raw.get("max_drawdown", 0.0), 0.0), 4)
    }

def normalize_trade_history(raw: Any) -> List[Dict[str, Any]]:
    rows = raw if isinstance(raw, list) else []
    out = []
    for row in rows:
        if isinstance(row, dict):
            out.append(row)
    return out

def normalize_market_state(raw: Dict[str, Any] | None) -> Dict[str, Any]:
    raw = raw or {}
    return {
        "status": raw.get("status", "idle"),
        "best_strategy": raw.get("best_strategy"),
        "strategy_results": raw.get("strategy_results", {}),
        "strategy_board": normalize_strategy_board(raw.get("strategy_board", {})),
        "genetics": normalize_genetics(raw.get("genetics", {})),
        "scan": _as_list(raw.get("scan", []), []),
        "signals": _as_list(raw.get("signals", []), []),
        "trades": _as_list(raw.get("trades", []), []),
        "score": raw.get("score", {}),
        "memory": normalize_memory(raw.get("memory", {})),
        "portfolio": normalize_portfolio(raw.get("portfolio", {})),
        "performance": normalize_performance(raw.get("performance", {})),
        "stats": raw.get("stats", {}),
        "updated_at": raw.get("updated_at"),
    }

