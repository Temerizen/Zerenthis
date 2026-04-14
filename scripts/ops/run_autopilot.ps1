cd C:\Zerenthis
.\venv\Scripts\activate
$env:PYTHONPATH = "$PWD\backend"
if (-not $env:AUTO_PUSH) { $env:AUTO_PUSH = "true" }
if (-not $env:AUTO_COMMIT_BRANCH) { $env:AUTO_COMMIT_BRANCH = "main" }
if (-not $env:AUTOPILOT_INTERVAL_SECONDS) { $env:AUTOPILOT_INTERVAL_SECONDS = "120" }
python backend/self_improver/autopilot.py
