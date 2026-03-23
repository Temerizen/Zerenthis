from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Zerenthis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Zerenthis API is live"}

@app.get("/command")
def command(q: str = ""):
    if not q:
        return {"response": "Command idle."}
    return {"response": f"Zerenthis processed: {q}"}