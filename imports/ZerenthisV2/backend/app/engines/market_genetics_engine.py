import random
from pathlib import Path
from typing import Dict, Any
from backend.app.engines.state_guard import safe_load_json, safe_save_json, normalize_genetics

DATA_DIR = Path("backend/data/market")
GENETICS_FILE = DATA_DIR / "strategy_genetics.json"

def load_genetics() -> Dict[str, Any]:
    return normalize_genetics(safe_load_json(GENETICS_FILE, {}))

def save_genetics(genetics: Dict[str, Any]):
    clean = normalize_genetics(genetics)
    safe_save_json(GENETICS_FILE, clean)

def _clamp(v, lo, hi):
    return max(lo, min(hi, v))

def mutate_value(v: float, strength: float = 0.15, lo: float = 0.25, hi: float = 15.0) -> float:
    delta = random.uniform(-strength, strength) * max(abs(v), 1.0)
    return round(_clamp(v + delta, lo, hi), 4)

def evolve_genetics(strategy_board: Dict[str, Any], genetics: Dict[str, Any]):
    genetics = normalize_genetics(genetics)
    strategies = (strategy_board or {}).get("strategies", {}) or {}
    if not strategies:
        save_genetics(genetics)
        return genetics

    ranked = sorted(
        strategies.items(),
        key=lambda x: (float(x[1].get("avg_profit", 0)), float(x[1].get("avg_winrate", 0))),
        reverse=True
    )

    best_name = ranked[0][0]
    worst_name = ranked[-1][0]
    best_gene = genetics.get(best_name, {}).copy()
    if not best_gene:
        save_genetics(genetics)
        return genetics

    genetics[worst_name] = {
        "threshold": mutate_value(float(best_gene.get("threshold", 2.0)), 0.20, 0.5, 8.0),
        "confidence_mult": mutate_value(float(best_gene.get("confidence_mult", 1.5)), 0.20, 0.5, 3.0),
        "max_conf": mutate_value(float(best_gene.get("max_conf", 10.0)), 0.10, 3.0, 10.0),
    }

    for name, gene in list(genetics.items()):
        if name == best_name:
            continue
        genetics[name] = {
            "threshold": mutate_value(float(gene.get("threshold", 2.0)), 0.05, 0.5, 8.0),
            "confidence_mult": mutate_value(float(gene.get("confidence_mult", 1.5)), 0.05, 0.5, 3.0),
            "max_conf": mutate_value(float(gene.get("max_conf", 10.0)), 0.03, 3.0, 10.0),
        }

    save_genetics(genetics)
    return genetics
