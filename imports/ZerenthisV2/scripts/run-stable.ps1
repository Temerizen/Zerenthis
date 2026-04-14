Set-Location $PSScriptRoot\..
.\venv\Scripts\python -m pip install -r .\backend\requirements.txt
Set-Location .\backend
..\venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
