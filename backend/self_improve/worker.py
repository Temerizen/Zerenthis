import time
from self_improve.generator import generate_patch
from self_improve.permission import classify_patch
from self_improve.apply import apply_patch
from self_improve.test_runner import run_tests
from self_improve.patch_queue import add_patch

def loop():
    while True:
        patch = generate_patch()
        decision = classify_patch(patch)

        if decision == "AUTO":
            if run_tests():
                apply_patch(patch)
                print("AUTO PATCH APPLIED:", patch["summary"])

        elif decision == "NEEDS_APPROVAL":
            add_patch(patch)
            print("WAITING FOR APPROVAL:", patch["summary"])

        elif decision == "BLOCKED":
            print("BLOCKED PATCH:", patch["summary"])

        time.sleep(60)
