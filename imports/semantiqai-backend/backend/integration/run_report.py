from backend.integration.doctor import run_doctor
from backend.integration.summary import integration_summary

if __name__ == "__main__":
    print("=== DOCTOR REPORT ===")
    print(run_doctor())
    print("=== SUMMARY ===")
    print(integration_summary())
