from self_improver.engine import create_proposal

# Inject high-value evolution tasks manually
ideas = [
    "Improve product packs with stronger emotional sales hooks and urgency",
    "Add high-conversion pricing tiers and bundle offers",
    "Upgrade PDF outputs with premium formatting and sections",
    "Add lead capture hooks to all generated outputs",
    "Improve YouTube script generation for higher retention and virality",
    "Add monetization metadata and CTA blocks to every output",
    "Enhance product titles to be more clickable and marketable",
    "Add scoring system to rank output quality automatically"
]

for idea in ideas:
    p = create_proposal({
        "title": idea,
        "description": idea,
        "tier": "low"
    })
    print("Injected:", p["id"])
