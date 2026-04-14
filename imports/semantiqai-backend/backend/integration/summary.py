from backend.integration.doctor import run_doctor
from backend.platform.logger import log_event

def integration_summary():
    report = run_doctor()
    log_event("integration_summary_generated", report)
    return report
