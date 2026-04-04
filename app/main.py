from fastapi import FastAPI

app = FastAPI(title="Zerenthis Autopilot", version="SAFE")

@app.get("/")
def root():
    return {"ok": True, "service": "autopilot", "mode": "safe"}

@app.get("/health")
def health():
    return {"ok": True, "service": "autopilot", "status": "healthy"}
