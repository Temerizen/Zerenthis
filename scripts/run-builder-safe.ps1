Set-Location C:\Zerenthis
$ErrorActionPreference = "Stop"
$env:BASE_URL = "http://127.0.0.1:8000"
python .\backend\architect_loop.py
