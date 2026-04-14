import os
import re
from datetime import datetime, timezone

OUTPUT_DIR = os.path.join("backend", "outputs", "money")

def _slugify(value: str) -> str:
    value = (value or "offer_stack").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "offer_stack"

def create_money_stack(topic: str, buyer: str = "general audience", price_anchor: str = "$19") -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    now = datetime.now(timezone.utc)
    slug = _slugify(topic)
    bundle = f"{slug}_{int(now.timestamp())}"
    bundle_dir = os.path.join(OUTPUT_DIR, bundle)
    os.makedirs(bundle_dir, exist_ok=True)

    files = {
        "offer_ladder.txt": f"Offer ladder for {topic}\n\nStarter: {price_anchor}\nGrowth: $49\nPremium: $99\n",
        "lead_magnet.txt": f"Lead magnet for {buyer}\n\nA short free asset that leads into the paid offer.\n",
        "email_funnel.txt": f"3-email funnel for {topic}\n\nEmail 1: problem\nEmail 2: solution\nEmail 3: CTA\n",
        "sales_angles.txt": f"Sales angles for {topic}\n\n- speed\n- simplicity\n- beginner-friendly outcome\n",
        "cta_pack.txt": f"CTA pack for {topic}\n\n- Start now\n- Get the pack\n- Use it today\n"
    }

    for name, content in files.items():
        with open(os.path.join(bundle_dir, name), "w", encoding="utf-8") as f:
            f.write(content)

    return {
        "status": "completed",
        "module": "money",
        "bundle": bundle,
        "files": [{"file_name": f"{bundle}/{k}", "file_url": f"/api/file/money/{bundle}/{k}"} for k in files.keys()]
    }

