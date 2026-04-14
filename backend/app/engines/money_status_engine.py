from backend.app.engines.module_snapshot_engine import module_snapshot

def get_money_status():
    return module_snapshot(
        "money",
        "Money Engine Active",
        "Offer, stack, and recurring money output systems are available.",
        score=8,
        metadata={"capabilities": ["product-pack", "money-stack", "winners"]}
    )

