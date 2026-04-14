def run_priority_engine():
    targets = []

    real = load_real_targets()
    seeds = generate_seed_targets()

    print("DEBUG REAL TARGETS:", real)
    print("DEBUG SEEDS:", seeds)

    targets.extend(real)
    targets.extend(seeds)

    print("DEBUG FINAL TARGET COUNT:", len(targets))

    scored = [score_target(t) for t in targets]
    ranked = sorted(scored, key=lambda x: x["total_score"], reverse=True)

    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "candidate_count": len(targets),
        "top_target": ranked[0] if ranked else None,
        "top_3": ranked[:3]
    }

    OUTPUT_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")

    return result
