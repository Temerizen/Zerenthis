from backend.app.core.output_engine import format_output
import os, time

def run_money(cycle_id):
    title = "AI Cashflow Micro-Product"

    output = format_output(
        title=title,
        summary="A ready-to-sell digital product generated automatically using AI systems.",
        steps=[
            "Pick a trending niche (AI, money, relationships)",
            "Generate a simple but valuable PDF guide",
            "Create viral short-form content for traffic",
            "Sell via Gumroad or Stripe instantly"
        ],
        monetization="Sell as $9-$29 digital product with upsells"
    )

    os.makedirs("backend/outputs", exist_ok=True)
    filename = f"backend/outputs/money_{int(time.time())}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(output))

    print(f"[MONEY][{cycle_id}] generated {filename}", flush=True)

    return {
        "status": "success",
        "file": filename,
        "data": output
    }
