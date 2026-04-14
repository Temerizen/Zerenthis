Set-Location $PSScriptRoot\..
if (!(Test-Path .\venv)) {
    python -m venv venv
}
.\venv\Scripts\python -m pip install -r .\backend\requirements.txt
Set-Location .\backend
..\venv\Scripts\python -m uvicorn app.main:app --reload
