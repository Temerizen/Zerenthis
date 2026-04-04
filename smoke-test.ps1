Set-Location C:\Zerenthis
$ErrorActionPreference = "Stop"

Write-Host "`nMAIN /health" -ForegroundColor Yellow
try { Invoke-RestMethod "http://127.0.0.1:8000/health" | ConvertTo-Json -Depth 8 } catch { Write-Host $_ -ForegroundColor Red }

Write-Host "`nAUTOPILOT /health" -ForegroundColor Yellow
try { Invoke-RestMethod "http://127.0.0.1:8010/health" | ConvertTo-Json -Depth 8 } catch { Write-Host $_ -ForegroundColor Red }

Write-Host "`nMAIN /api/founder/overview" -ForegroundColor Yellow
try { Invoke-RestMethod "http://127.0.0.1:8000/api/founder/overview" | ConvertTo-Json -Depth 8 } catch { Write-Host $_ -ForegroundColor Red }
