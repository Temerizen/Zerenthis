from backend.app.core.output_engine import format_output
import os, time

def run_money(cycle_id):
    title = "Instant Cashflow Offer"

    output = format_output(
        title=title,
        summary="A fast-launch digital offer designed to generate immediate revenue using AI content systems.",
        steps=[
            "Create simple digital product",
            "Use TikTok or Shorts for traffic",
            "Offer limited-time deal",
            "Drive to Gumroad or Stripe"
        ],
        monetization="Direct digital product sales and affiliate stacking"
    )

    os.makedirs("backend/outputs", exist_ok=True)
    filename = f"backend/outputs/money_{int(time.time())}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(output))

    print(f"[MONEY][{cycle_id}] generated {filename}", flush=True)
