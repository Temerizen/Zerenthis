Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "Stopped all python processes." -ForegroundColor Yellow
