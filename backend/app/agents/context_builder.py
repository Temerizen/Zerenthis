from typing import List, Dict

def build_context_block(short_term: List[Dict], long_term: List[Dict]) -> str:
    parts = []

    if short_term:
        parts.append("SHORT TERM MEMORY:")
        for item in short_term:
            parts.append(f"- ({item.get('role', 'unknown')}) {item.get('content', '')}")

    if long_term:
        parts.append("")
        parts.append("LONG TERM MEMORY:")
        for item in long_term:
            parts.append(f"- [{item.get('category', 'general')}] {item.get('content', '')}")

    return "\n".join(parts).strip()

