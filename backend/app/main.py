# ----------------------------
# 🧠 GROWTH ENGINE
# ----------------------------
def get_growth_topics(niche="ai"):
    base = {
        "ai": [
            "AI automation",
            "making money with AI",
            "AI replacing jobs",
            "AI business ideas",
            "AI side hustles"
        ],
        "business": [
            "making money online",
            "side hustles",
            "passive income",
            "digital products",
            "scaling a business"
        ],
        "self": [
            "discipline",
            "focus",
            "dopamine",
            "productivity",
            "self improvement"
        ]
    }

    return base.get(niche, base["ai"])