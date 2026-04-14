cd C:\Zerenthis
.\venv\Scripts\activate
$env:PYTHONPATH = "$PWD\backend"
python -m uvicorn backend.app.main:app
