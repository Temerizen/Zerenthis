PRESETS = {
    "product_blueprint": {
        "title": "Product Blueprint",
        "description": "Creates a product concept, positioning, structure, and delivery outline."
    },
    "content_pack": {
        "title": "Content Pack",
        "description": "Creates a content strategy, content ideas, and execution-ready pieces."
    },
    "brand_strategy": {
        "title": "Brand Strategy",
        "description": "Creates brand positioning, messaging, voice, and identity direction."
    },
    "research_brief": {
        "title": "Research Brief",
        "description": "Creates a research summary, options analysis, and recommendation set."
    },
    "founder_os": {
        "title": "Founder Operating System",
        "description": "Creates a founder plan, priorities, systems, routines, and execution map."
    }
}

def list_presets():
    return PRESETS

def get_preset(name: str):
    return PRESETS.get(name)

