from fastapi import FastAPI

app = FastAPI(title="Zerenthis Autopilot", version="FINAL")

@app.get("/")
def root():
    return {"ok": True, "service": "autopilot alive"}

@app.get("/health")
def health():
    return {"ok": True, "service": "autopilot alive"}
