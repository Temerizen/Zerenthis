from backend.memory.short_term import remember
from backend.memory.long_term import save_long_term
from backend.services.router import select_agent, get_agent
from backend.services.context_service import build_context
import sqlite3
from backend.core.config import DB_PATH

def _log_prompt_run(agent: str, prompt: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO prompt_runs (agent, prompt) VALUES (?, ?)",
        (agent, prompt)
    )
    conn.commit()
    conn.close()

def run_prompt(prompt: str, force_agent: str | None = None, remember_output: bool = True):
    chosen_agent = force_agent or select_agent(prompt)
    agent_fn = get_agent(chosen_agent)
    context = build_context()

    remember("user", prompt, category=chosen_agent)
    _log_prompt_run(chosen_agent, prompt)

    result = agent_fn(prompt=prompt, context=context)

    if remember_output:
        remember("assistant", result.output, category=chosen_agent)
        save_long_term(chosen_agent, prompt)

    return result.to_dict()

