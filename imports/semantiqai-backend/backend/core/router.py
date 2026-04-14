def route(msg: str) -> str:
    m = (msg or "").lower()

    if any(k in m for k in ["plan", "roadmap", "strategy", "steps", "outline"]):
        return "planner"
    if any(k in m for k in ["research", "analyze", "compare", "market", "opportunity", "brief"]):
        return "research"
    if any(k in m for k in ["brand", "branding", "positioning", "voice", "identity"]):
        return "brand"
    if any(k in m for k in ["content", "posts", "captions", "newsletter", "youtube", "tiktok"]):
        return "content"
    if any(k in m for k in ["product", "offer", "service", "bundle", "ebook", "guide"]):
        return "product"
    if any(k in m for k in ["execute", "build", "write", "generate", "make"]):
        return "execution"
    if any(k in m for k in ["code", "python", "javascript", "bug", "debug", "flask", "react", "html", "css", "sql"]):
        return "coding"
    if any(k in m for k in ["acting", "audition", "scene", "monologue", "self tape"]):
        return "acting"
    if any(k in m for k in ["money", "finance", "invest", "budget", "income", "profit", "side hustle"]):
        return "finance"
    if any(k in m for k in ["job", "career", "resume", "interview", "linkedin"]):
        return "career"
    if any(k in m for k in ["health", "fitness", "diet", "workout", "sleep"]):
        return "health"

    return "general"

