import json
import os
import random

GENETICS_FILE = os.path.join("backend","data","strategy_genetics.json")

def load_genetics():
    if not os.path.exists(GENETICS_FILE):
        return {}
    with open(GENETICS_FILE, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_genetics(data):
    with open(GENETICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def adjust_gene(gene, factor, lo=0.8, hi=3.0):
    return round(min(hi, max(lo, gene * factor)), 4)

def evolve_strategies(strategy_results):
    genetics = load_genetics()

    for name, strat in strategy_results.get("strategies", {}).items():
        profit = float(strat.get("profit", 0))
        winrate = float(strat.get("winrate", 0))

        gene = genetics.get(name, strat.get("gene", {}))

        threshold = float(gene.get("threshold", 1.5))
        confidence_mult = float(gene.get("confidence_mult", 1.5))

        # 🧠 reward / punish logic
        if profit > 0:
            threshold = adjust_gene(threshold, 0.98, 0.8, 3.0)
            confidence_mult = adjust_gene(confidence_mult, 1.02, 0.8, 2.2)
        else:
            threshold = adjust_gene(threshold, 1.05, 0.8, 3.0)
            confidence_mult = adjust_gene(confidence_mult, 0.95, 0.8, 2.2)

        # small mutation for exploration
        threshold *= random.uniform(0.98, 1.02)
        confidence_mult *= random.uniform(0.98, 1.02)

        genetics[name] = {
            "threshold": round(threshold, 4),
            "confidence_mult": round(confidence_mult, 4),
            "max_conf": gene.get("max_conf", 10.0)
        }

    save_genetics(genetics)
    return genetics

