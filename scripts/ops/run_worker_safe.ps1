cd C:\Zerenthis
.\venv\Scripts\activate
$env:PYTHONPATH = "$PWD\backend"
python backend/self_improver/worker.py
