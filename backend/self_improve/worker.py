import json
import time
from pathlib import Path

from self_improve.generator import generate_patch
from self_improve.permission import classify_patch
from self_improve.apply import apply_patch
from self_improve.test_runner import run_tests
from self_improve.patch_queue import add_patch
from self_improve.logger import log

POLICY = json.loads(Path("backend/self_improve/policy.json").read_text(encoding="utf-8"))


def loop():
    log("Worker started.")

    while True:
        try:
            patch = generate_patch()

            if not patch.get("files"):
                log("No eligible patch generated.")
                time.sleep(POLICY["loop_interval_seconds"])
                continue

            decision = classify_patch(patch)
            log(f"Patch generated: {patch['summary']} | decision={decision}")

            if decision == "AUTO":
                ok, checks = run_tests()
                log(f"Test results before apply: {checks}")

                if ok:
                    result = apply_patch(patch)
                    log(f"Auto patch applied: {patch['summary']} | result={result}")
                else:
                    log(f"Auto patch rejected due to failed tests: {checks}")

            elif decision == "NEEDS_APPROVAL":
                patch_id = add_patch(patch)
                log(f"Patch queued for approval: {patch['summary']} | id={patch_id}")

            elif decision == "BLOCKED":
                log(f"Blocked patch: {patch['summary']}")

        except Exception as e:
            log(f"Worker error: {e}")

        time.sleep(POLICY["loop_interval_seconds"])


if __name__ == "__main__":
    loop()
