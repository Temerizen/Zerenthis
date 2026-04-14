def run_performance_cycle():
    print("PERFORMANCE cycle...")

    try:
        from self_improver.outcome_engine import evaluate_and_improve
    except:
        print("No outcome engine found, skipping...")
        return {"ok": False}

    try:
        result = evaluate_and_improve()
        print("RESULT:", result)
        return result
    except Exception as e:
        print("ERROR:", e)
        return {"ok": False, "error": str(e)}
