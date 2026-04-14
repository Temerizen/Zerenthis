def run_automation(workflow):
    results = []
    for step in workflow.get("steps", []):
        results.append(f"Executed: {step}")
    return results

