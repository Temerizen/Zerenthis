Set-Location $PSScriptRoot\..
while ($true) {
    try {
        Set-Location .\backend
        ..\venv\Scripts\python -c "from app.core.worker import process_next_job; print(process_next_job())"
        Set-Location ..
    } catch {
        Write-Host "Worker error: $(.Exception.Message)" -ForegroundColor Red
    }
    Start-Sleep -Seconds 3
}
