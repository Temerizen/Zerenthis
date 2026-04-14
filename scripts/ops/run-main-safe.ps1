Set-Location C:\Zerenthis
$ErrorActionPreference = "Stop"
$env:PUBLIC_BASE_URL = "https://api.zerenthis.com"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
