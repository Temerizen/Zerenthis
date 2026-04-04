Set-Location C:\Zerenthis
$ErrorActionPreference = "Stop"

$backendPy = $null
if (Test-Path ".\venv\Scripts\python.exe") {
    $backendPy = ".\venv\Scripts\python.exe"
} elseif (Test-Path ".\.venv\Scripts\python.exe") {
    $backendPy = ".\.venv\Scripts\python.exe"
} else {
    $backendPy = "python"
}

Start-Process powershell -ArgumentList "-NoExit","-Command","Set-Location C:\Zerenthis; $backendPy -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"
Start-Sleep 4

if (Test-Path ".\frontend") {
    Start-Process powershell -ArgumentList "-NoExit","-Command","Set-Location C:\Zerenthis\frontend; npm run dev"
}

Start-Sleep 6

if (!(Test-Path ".\desktop\node_modules")) {
    Start-Process powershell -ArgumentList "-NoExit","-Command","Set-Location C:\Zerenthis\desktop; npm install"
    Write-Host "Desktop dependencies installing in a new window. After install completes, rerun this launcher." -ForegroundColor Yellow
} else {
    Start-Process powershell -ArgumentList "-NoExit","-Command","Set-Location C:\Zerenthis\desktop; `$env:ZERENTHIS_FRONTEND_URL='http://127.0.0.1:5173'; npm start"
}
