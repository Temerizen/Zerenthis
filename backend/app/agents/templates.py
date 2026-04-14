TEMPLATES = {
    "service_offer": "# Service Offer\n\n## Offer\n\n## Audience\n\n## Pricing Logic\n\n## Delivery\n",
    "research_report": "# Research Report\n\n## Objective\n\n## Findings\n\n## Options\n\n## Recommendation\n",
    "brand_doc": "# Brand Document\n\n## Positioning\n\n## Voice\n\n## Messaging\n\n## Offer Direction\n",
    "founder_plan": "# Founder Plan\n\n## Priority Stack\n\n## Systems\n\n## Weekly Cadence\n\n## Execution Rules\n"
}

def list_templates():
    return TEMPLATES

def get_template(name: str):
    return TEMPLATES.get(name)


