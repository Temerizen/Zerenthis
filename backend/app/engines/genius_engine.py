from backend.app.core.output_engine import format_output

def run_genius(problem):
    return format_output(
        title=f"Genius Solution: {problem}",
        summary="Advanced reasoning applied to complex real-world or scientific problems.",
        steps=[
            "Deconstruct the problem",
            "Explore unconventional angles",
            "Simulate outcomes",
            "Propose breakthrough solution"
        ],
        monetization="Licensing ideas or consulting"
    )

