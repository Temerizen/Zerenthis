import os
from fastapi import FastAPI

app = FastAPI(title="Zerenthis Autopilot")

@app.get("/")
def root():
    return {"ok": True, "service": "autopilot"}

@app.get("/health")
def health():
    return {"ok": True, "service": "autopilot"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
