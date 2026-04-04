import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"

EXPECTED_BACKEND_MODULES = [
    "cognitive_lab",
    "ai_school",
    "execution_engine",
    "simulation_engine",
    "creation_engine",
    "founder_video",
    "founder_distribution",
    "founder_panel",
    "auth_system",
    "stabilization",
    "platform"
]

EXPECTED_FRONTEND_FILES = [
    FRONTEND / "package.json",
    FRONTEND / "src" / "App.jsx",
    FRONTEND / "src" / "main.jsx",
    FRONTEND / "src" / "config" / "api.js",
]

def run_doctor():
    report = {
        "backend_modules": [],
        "frontend_files": [],
        "warnings": []
    }

    for name in EXPECTED_BACKEND_MODULES:
        p = BACKEND / name
        report["backend_modules"].append({
            "name": name,
            "exists": p.exists()
        })
        if not p.exists():
            report["warnings"].append(f"Missing backend module: {name}")

    for p in EXPECTED_FRONTEND_FILES:
        report["frontend_files"].append({
            "path": str(p.relative_to(ROOT)),
            "exists": p.exists()
        })
        if not p.exists():
            report["warnings"].append(f"Missing frontend file: {p.relative_to(ROOT)}")

    return report

if __name__ == "__main__":
    print(json.dumps(run_doctor(), indent=2))
