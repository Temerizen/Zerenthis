from fastapi import FastAPI

app = FastAPI(title="Zerenthis Autopilot", version="1.3")

@app.get("/")
def root():
    return {"ok": True, "service": "autopilot"}

@app.get("/health")
def health():
    return {"ok": True, "service": "autopilot"}
