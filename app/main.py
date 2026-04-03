from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "builder live"}

@app.get("/health")
def health():
    return {"ok": True}
