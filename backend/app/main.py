from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"ok": True, "message": "root alive"}

@app.get("/health")
def health():
    return {"ok": True, "message": "health alive"}
