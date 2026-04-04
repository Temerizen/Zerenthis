Set-Location C:\Zerenthis
$ErrorActionPreference = "Stop"
$env:PUBLIC_BASE_URL = "https://api.zerenthis.com"
python -m backend.architect_loop
