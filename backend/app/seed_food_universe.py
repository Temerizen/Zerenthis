import os, json, textwrap, random

BASE = os.path.dirname(__file__)
GEN = os.path.join(BASE, "generated")
os.makedirs(GEN, exist_ok=True)

SYSTEMS = {
    "seed_money_offer_generator.py": '''
def run():
    niche = "AI productivity for solo founders"
    return {
        "ok": True,
        "title": "Founder Fast-Cash Offer Builder",
        "summary": "Generates a sellable offer with promise, buyer, bonus, and CTA.",
        "offer": {
            "buyer": "solo founder overwhelmed by content and sales",
            "problem": "too many ideas, not enough execution",
            "promise": "launch a simple paid offer in 24 hours",
            "product": "Offer Blueprint PDF + scripts + launch checklist",
            "price": 29,
            "bonus": "10 urgency hooks and 5 CTA variations",
            "cta": "Sell the blueprint as a same-day starter kit"
        },
        "category": "money",
        "value_score_hint": 9
    }
''',
    "seed_product_pack_generator.py": '''
def run():
    topic = "Faceless short-form video monetization"
    return {
        "ok": True,
        "title": "Premium Product Pack Generator",
        "summary": "Creates a structured digital product concept suitable for immediate sale.",
        "pack": {
            "topic": topic,
            "components": [
                "core PDF guide",
                "30 hook lines",
                "10 CTA scripts",
                "thumbnail/title ideas",
                "launch checklist"
            ],
            "buyer": "beginner creator",
            "price_range": "$19-$49",
            "positioning": "fast-start monetization pack"
        },
        "category": "product",
        "value_score_hint": 9
    }
''',
    "seed_content_calendar.py": '''
def run():
    return {
        "ok": True,
        "title": "30-Day Content Calendar",
        "summary": "Builds a practical 30-day content plan with hooks, formats, and calls to action.",
        "days": [
            {"day": 1, "format": "short video", "hook": "Why most people fail before post one", "cta": "comment START"},
            {"day": 2, "format": "carousel", "hook": "3 mistakes beginners make instantly", "cta": "save this"},
            {"day": 3, "format": "thread", "hook": "How to build a tiny offer from one problem", "cta": "DM OFFER"}
        ],
        "category": "content",
        "value_score_hint": 8
    }
''',
    "seed_research_synthesizer.py": '''
def run():
    return {
        "ok": True,
        "title": "Research Synthesis Engine",
        "summary": "Returns a structured analysis shell with thesis, key findings, applications, and open questions.",
        "analysis": {
            "thesis": "Systems improve when generation, evaluation, and selection are connected.",
            "key_findings": [
                "High-volume generation without selection creates clutter.",
                "Clear scoring criteria create evolutionary pressure.",
                "Useful templates outperform placeholder outputs."
            ],
            "applications": [
                "content systems",
                "product generation",
                "autonomous builders",
                "research assistants"
            ],
            "open_questions": [
                "How should mutation be constrained?",
                "What scoring metrics best predict usefulness?"
            ]
        },
        "category": "research",
        "value_score_hint": 8
    }
''',
    "seed_hook_library.py": '''
def run():
    return {
        "ok": True,
        "title": "Hook Library",
        "summary": "Produces reusable hooks for content, offers, and product landing pages.",
        "hooks": [
            "Most people are doing this backwards.",
            "This is the shortcut nobody explains clearly.",
            "You do not need more motivation. You need this system.",
            "The fastest way to get your first result is simpler than you think.",
            "This turns scattered effort into a real asset."
        ],
        "category": "copywriting",
        "value_score_hint": 7
    }
''',
    "seed_landing_page_copy.py": '''
def run():
    return {
        "ok": True,
        "title": "Landing Page Copy Draft",
        "summary": "Creates a basic headline, subheadline, bullets, and CTA for a digital product.",
        "copy": {
            "headline": "Turn one idea into a product you can sell this week",
            "subheadline": "Zerenthis helps founders generate offers, content, and launch assets without drowning in complexity.",
            "bullets": [
                "Generate a focused offer in minutes",
                "Get content and promotion assets instantly",
                "Use execution-ready outputs instead of vague ideas"
            ],
            "cta": "Generate My Starter Pack"
        },
        "category": "copywriting",
        "value_score_hint": 8
    }
''',
    "seed_email_sequence.py": '''
def run():
    return {
        "ok": True,
        "title": "3-Email Sales Sequence",
        "summary": "Drafts a simple nurture-to-sale sequence for a starter digital product.",
        "emails": [
            {"subject": "The easiest offer to launch first", "goal": "belief shift"},
            {"subject": "Why simple beats clever at the beginning", "goal": "objection handling"},
            {"subject": "Your starter pack is ready", "goal": "conversion"}
        ],
        "category": "email",
        "value_score_hint": 8
    }
''',
    "seed_gumroad_pack.py": '''
def run():
    return {
        "ok": True,
        "title": "Gumroad Pack Blueprint",
        "summary": "Returns a ready-to-sell asset structure for a digital marketplace listing.",
        "gumroad_pack": {
            "name": "Zero-to-Offer Starter Pack",
            "includes": [
                "20-page PDF",
                "50 hooks",
                "10 email prompts",
                "launch checklist"
            ],
            "price": 19,
            "thumbnail_text": "Launch in 24 Hours",
            "description": "A compact system for turning one problem into a small sellable product."
        },
        "category": "marketplace",
        "value_score_hint": 9
    }
''',
    "seed_video_script_pack.py": '''
def run():
    return {
        "ok": True,
        "title": "Short Video Script Pack",
        "summary": "Creates short-form scripts designed for no-face or voiceover content.",
        "scripts": [
            {"title": "Stop Overcomplicating Your First Offer", "script": "You do not need a brand empire. You need one clear problem and one simple solution."},
            {"title": "The Fastest Way to Make a Product Tonight", "script": "Start with the promise, then the proof, then the CTA. Everything else comes later."},
            {"title": "Why Most Builders Stay Broke", "script": "They keep making systems for themselves instead of assets people can buy."}
        ],
        "category": "video",
        "value_score_hint": 8
    }
''',
    "seed_plan_generator.py": '''
def run():
    return {
        "ok": True,
        "title": "Execution Plan Generator",
        "summary": "Creates a practical action plan with milestones and outcomes.",
        "plan": {
            "goal": "launch a digital starter product",
            "milestones": [
                "pick one buyer problem",
                "create offer statement",
                "assemble core asset",
                "write landing copy",
                "publish and promote"
            ],
            "timeframe": "24-72 hours"
        },
        "category": "planning",
        "value_score_hint": 8
    }
''',
    "seed_mutation_template.py": '''
def run():
    return {
        "ok": True,
        "title": "Mutation Template",
        "summary": "A meta-template that suggests how a winning system could be varied.",
        "mutations": [
            "change target buyer",
            "change price point",
            "change delivery format",
            "change promise intensity",
            "add niche-specific examples"
        ],
        "category": "evolution",
        "value_score_hint": 7
    }
''',
    "seed_offer_angle_finder.py": '''
def run():
    return {
        "ok": True,
        "title": "Offer Angle Finder",
        "summary": "Generates multiple ways to frame the same product for different buyers.",
        "angles": [
            "speed angle: get your first offer live tonight",
            "simplicity angle: one product, one page, one CTA",
            "clarity angle: stop drowning in ideas and pick one",
            "profit angle: small digital asset, fast turnaround"
        ],
        "category": "positioning",
        "value_score_hint": 8
    }
''',
    "seed_objection_handler.py": '''
def run():
    return {
        "ok": True,
        "title": "Objection Handler",
        "summary": "Maps common buyer objections to concise responses.",
        "objections": [
            {"objection": "I do not have an audience", "response": "Start with direct outreach and focused distribution, not broad brand-building."},
            {"objection": "I am not an expert", "response": "Sell structured clarity and action steps, not pretend omniscience."},
            {"objection": "I have too many ideas", "response": "Choose the one closest to immediate pain and fastest delivery."}
        ],
        "category": "sales",
        "value_score_hint": 8
    }
''',
    "seed_bundle_builder.py": '''
def run():
    return {
        "ok": True,
        "title": "Bundle Builder",
        "summary": "Combines related assets into a higher-value package.",
        "bundle": {
            "core": "starter guide",
            "add_ons": ["script pack", "email sequence", "landing page copy", "launch checklist"],
            "bundle_price": 49,
            "why_it_sells": "reduces decision friction and increases perceived completeness"
        },
        "category": "bundling",
        "value_score_hint": 8
    }
''',
    "seed_thumbnail_title_generator.py": '''
def run():
    return {
        "ok": True,
        "title": "Thumbnail + Title Generator",
        "summary": "Creates click-oriented titles and thumbnail phrases.",
        "ideas": [
            {"title": "Launch a Digital Product Tonight", "thumbnail": "24 HOUR LAUNCH"},
            {"title": "Stop Building, Start Selling", "thumbnail": "SELL FIRST"},
            {"title": "One Offer. One Page. One Sale.", "thumbnail": "KEEP IT SIMPLE"}
        ],
        "category": "media",
        "value_score_hint": 7
    }
''',
    "seed_audience_problem_map.py": '''
def run():
    return {
        "ok": True,
        "title": "Audience Problem Map",
        "summary": "Maps buyer types to urgent pains and possible products.",
        "map": [
            {"buyer": "new creator", "pain": "inconsistent posting", "product": "content starter kit"},
            {"buyer": "solo founder", "pain": "unclear offer", "product": "offer blueprint"},
            {"buyer": "freelancer", "pain": "unreliable leads", "product": "outreach script pack"}
        ],
        "category": "market",
        "value_score_hint": 8
    }
''',
    "seed_mini_consultation_generator.py": '''
def run():
    return {
        "ok": True,
        "title": "Mini Consultation Generator",
        "summary": "Produces a short diagnosis and recommended action path.",
        "diagnosis": {
            "problem": "too much generation, not enough focused monetization",
            "why": "outputs are not being shaped around buyer value",
            "recommendation": "prioritize small offers and structured content assets"
        },
        "category": "consulting",
        "value_score_hint": 8
    }
'''
}

for name, content in SYSTEMS.items():
    path = os.path.join(GEN, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(content).strip() + "\\n")

manifest = {
    "ok": True,
    "seeded_files": sorted(list(SYSTEMS.keys())),
    "count": len(SYSTEMS),
    "categories": sorted(list(set([
        "money","product","content","research","copywriting","email","marketplace","video",
        "planning","evolution","positioning","sales","bundling","media","market","consulting"
    ])))
}

with open(os.path.join(os.path.dirname(BASE), "data", "seed_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(json.dumps(manifest, indent=2))
