$root = "C:\Zerenthis"

Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$root`"; .\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"
Start-Sleep -Seconds 3
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$root`"; .\venv\Scripts\python.exe -m backend.self_improver.worker"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$root`"; .\venv\Scripts\python.exe -m backend.self_improver.autopilot"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$root`"; .\venv\Scripts\python.exe -m backend.empire.loop"

Write-Host "Empire stack launched." -ForegroundColor Green
Write-Host "API: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
