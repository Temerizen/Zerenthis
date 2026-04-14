from backend.app.core.output_engine import format_output

def run_builder(cycle_id):
    idea = "Faceless Viral Content System"

    return format_output(
        title=idea,
        summary="A viral-ready system to generate high-engagement content automatically across platforms.",
        steps=[
            "Pick niche with emotional pull",
            "Generate viral hooks",
            "Produce short-form content daily",
            "Repurpose across platforms"
        ],
        monetization="Sell digital packs or monetize traffic via TikTok Creativity Program"
    )


