from backend.memory.short_term import recall as recall_short
from backend.memory.long_term import recall_long_term
from backend.utils.context_builder import build_context_block

def build_context(short_limit: int = 8, long_limit: int = 8, category: str | None = None) -> str:
    short_items = recall_short(limit=short_limit, category=category)
    long_items = recall_long_term(limit=long_limit, category=category)
    return build_context_block(short_items, long_items)

