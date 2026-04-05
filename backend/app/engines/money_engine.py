from backend.app.core.output_engine import format_output
from backend.app.engines.pdf_engine import create_pdf
from backend.app.engines.sell_engine import generate_offer

def run_money(cycle_id):
    product = format_output(
        title="Faceless Content Cashflow Kit",
        summary="A plug-and-play system to generate viral content and monetize instantly.",
        steps=[
            "Pick a viral niche",
            "Use AI to generate scripts",
            "Post 3-5 short videos daily",
            "Redirect traffic to digital product"
        ],
        monetization="Sell as a $19-$49 digital product via Gumroad or Stripe"
    )

    pdf = create_pdf(product)
    offer = generate_offer(product)

    print(f"[MONEY][{cycle_id}] SELLABLE PRODUCT → {pdf}", flush=True)

    return {
        "status": "success",
        "file": pdf,
        "product": product,
        "offer": offer
    }
