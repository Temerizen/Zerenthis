Set-Location C:\Zerenthis
Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|powershell' -and $_.CommandLine -match 'uvicorn backend.app.main:app --host 127.0.0.1 --port 8000' } | ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force } catch {} }
Start-Process powershell -ArgumentList '-NoExit','-Command','Set-Location ''C:\Zerenthis''; .\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000'
Start-Sleep 6
Start-Process 'http://127.0.0.1:8000'
