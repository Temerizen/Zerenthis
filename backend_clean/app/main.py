from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Zerenthis staging backend live"}

@app.get("/health")
def health():
    return {"ok": True}