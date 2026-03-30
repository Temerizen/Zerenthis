from __future__ import annotations

import time

from self_improver.engine import approved, execute

def run():
    print("Autopilot started. Watching for approved proposals...")
    seen = set()

    while True:
        try:
            for proposal in approved():
                pid = proposal.get("id")
                if not pid or pid in seen:
                    continue

                meta = proposal.get("meta", {}) or {}
                policy = meta.get("policy", {}) or {}

                print(
                    "Executing:",
                    pid,
                    "-",
                    proposal.get("title"),
                    "| tier:",
                    policy.get("tier", "unknown"),
                    "| risk:",
                    policy.get("risk_score", "?"),
                )

                result = execute(pid)
                print("Result:", result)
                seen.add(pid)

        except Exception as e:
            print("AUTOPILOT ERROR:", e)

        time.sleep(15)

if __name__ == "__main__":
    run()

