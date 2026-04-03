from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.adaptive_brain import router as adaptive_brain_router

app = FastAPI(title="Zerenthis Brain Runner", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(adaptive_brain_router)

@app.get("/")
def root():
    return {"status": "ok", "message": "brain runner live"}
