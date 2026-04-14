def build_scenario(name: str, domain: str, objective: str, constraints: list[str]) -> dict:
    return {
        "title": f"{name} | simulation",
        "domain": domain,
        "objective": objective,
        "constraints": constraints,
        "phases": [
            "Define starting conditions",
            "Identify leverage points",
            "Map primary risks",
            "Run best case path",
            "Run realistic path",
            "Run failure path",
            "Summarize recommended moves"
        ],
        "recommendations": [
            f"Start with the highest leverage action in {domain}",
            "Reduce friction before scaling",
            "Track one core metric and one failure metric",
            "Use short iteration loops"
        ]
    }

def render_scenario_markdown(data: dict) -> str:
    constraints = "\n".join([f"- {x}" for x in data["constraints"]]) if data["constraints"] else "- none provided"
    phases = "\n".join([f"- {x}" for x in data["phases"]])
    recommendations = "\n".join([f"- {x}" for x in data["recommendations"]])

    return f"""# {data['title']}

## Domain
{data['domain']}

## Objective
{data['objective']}

## Constraints
{constraints}

## Simulation Phases
{phases}

## Recommended Moves
{recommendations}
"""

