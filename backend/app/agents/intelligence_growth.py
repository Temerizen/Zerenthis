import json
import re

def safe_json_loads(value, default):
    try:
        return json.loads(value or "")
    except Exception:
        return default

def tokenize(text):
    return re.findall(r"[a-zA-Z0-9_]+", (text or "").lower())

def clip(text, limit=400):
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."

def fetch_profile_context(conn, user_id):
    try:
        row = conn.execute(
            "SELECT goals, preferences, traits, updated_at FROM user_profiles WHERE user_id = ?",
            (user_id,)
        ).fetchone()
    except Exception:
        return {"goals": [], "preferences": [], "traits": [], "updated_at": ""}

    if not row:
        return {"goals": [], "preferences": [], "traits": [], "updated_at": ""}

    return {
        "goals": safe_json_loads(row["goals"], []),
        "preferences": safe_json_loads(row["preferences"], []),
        "traits": safe_json_loads(row["traits"], []),
        "updated_at": row["updated_at"] or ""
    }

def fetch_relevant_memory(conn, user_id, query, limit=6):
    try:
        rows = conn.execute(
            "SELECT id, thread_id, memory_type, title, content, tags, score, created_at "
            "FROM memory_items WHERE user_id = ? ORDER BY score DESC, id DESC LIMIT 250",
            (user_id,)
        ).fetchall()
    except Exception:
        return []

    q_tokens = set(tokenize(query))
    scored = []

    for row in rows:
        item = dict(row)
        tags = safe_json_loads(item.get("tags"), [])
        hay = " ".join([
            str(item.get("title") or ""),
            str(item.get("content") or ""),
            " ".join(tags)
        ]).lower()

        overlap = len(q_tokens.intersection(set(tokenize(hay))))
        base = float(item.get("score") or 1.0)
        total = base + (overlap * 2.0)
        if overlap > 0 or base >= 2.5:
            item["tags"] = tags
            item["_score"] = total
            scored.append(item)

    scored.sort(key=lambda x: (x["_score"], x.get("id", 0)), reverse=True)
    return scored[:limit]

def compose_intelligence_prompt(conn, user_id, message, thread_id=None):
    profile = fetch_profile_context(conn, user_id)
    memories = fetch_relevant_memory(conn, user_id, message, limit=6)

    profile_lines = []
    if profile["goals"]:
        profile_lines.append("Goals: " + ", ".join(profile["goals"][:8]))
    if profile["preferences"]:
        profile_lines.append("Preferences: " + ", ".join(profile["preferences"][:8]))
    if profile["traits"]:
        profile_lines.append("Traits: " + ", ".join(profile["traits"][:8]))

    memory_lines = []
    for m in memories:
        title = m.get("title") or "Memory"
        content = clip(m.get("content") or "", 220)
        tags = ", ".join((m.get("tags") or [])[:5])
        extras = f" | tags: {tags}" if tags else ""
        memory_lines.append(f"- {title}: {content}{extras}")

    context_parts = []
    if profile_lines:
        context_parts.append("User Profile Context:\n" + "\n".join(profile_lines))
    if memory_lines:
        context_parts.append("Relevant Long-Term Memory:\n" + "\n".join(memory_lines))

    if not context_parts:
        return message, {"profile_used": False, "memory_count": 0}

    enriched = (
        "Use the following user context when it genuinely helps. "
        "Do not mention hidden memory or profile data explicitly unless the user asks.\n\n"
        + "\n\n".join(context_parts)
        + "\n\nCurrent User Request:\n"
        + message
    )
    return enriched, {
        "profile_used": bool(profile_lines),
        "memory_count": len(memory_lines)
    }

def extract_memory_candidates(message, response):
    text = (message or "").strip()
    lowered = text.lower()
    candidates = []

    patterns = [
        ("goal", r"(?:my goal is|i want to|i'm trying to|i am trying to)\s+(.+)", 3.2, ["goal", "user"]),
        ("preference", r"(?:i prefer|please always|from now on|remember that)\s+(.+)", 3.6, ["preference", "user"]),
        ("identity", r"(?:i am|i'm)\s+(.+)", 2.0, ["identity", "user"]),
        ("project", r"(?:my project is|i'm building|i am building|working on)\s+(.+)", 3.0, ["project", "user"]),
    ]

    for memory_type, pattern, score, tags in patterns:
        m = re.search(pattern, lowered, re.IGNORECASE)
        if m:
            raw = text[m.start(1):].strip(" .,!?\t\r\n")
            if 8 <= len(raw) <= 240:
                candidates.append({
                    "memory_type": memory_type,
                    "title": memory_type.title(),
                    "content": raw,
                    "tags": tags,
                    "score": score
                })

    if "remember" in lowered and len(text) <= 280 and not candidates:
        candidates.append({
            "memory_type": "explicit_memory",
            "title": "Explicit Memory",
            "content": text,
            "tags": ["remember", "user"],
            "score": 4.0
        })

    return candidates[:4]

def store_memory_candidates(conn, user_id, thread_id, message, response):
    items = extract_memory_candidates(message, response)
    for item in items:
        conn.execute(
            "INSERT INTO memory_items (user_id, thread_id, memory_type, title, content, tags, score, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
            (
                user_id,
                thread_id,
                item["memory_type"],
                item["title"],
                item["content"],
                json.dumps(item["tags"]),
                item["score"]
            )
        )
    return len(items)

def create_growth_event(conn, event_type, source, meta=None, user_id=None):
    payload = json.dumps(meta or {})
    conn.execute(
        "INSERT INTO growth_events (user_id, event_type, source, payload_json, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
        (user_id, event_type, source, payload)
    )

def stream_chunks(text, max_words=8):
    words = (text or "").split()
    if not words:
        return []
    chunks = []
    buf = []
    for word in words:
        buf.append(word)
        if len(buf) >= max_words:
            chunks.append(" ".join(buf) + " ")
            buf = []
    if buf:
        chunks.append(" ".join(buf))
    return chunks

