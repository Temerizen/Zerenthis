from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ? CORS FIX (allows your Vercel frontend to talk to backend)
origins = [
    "https://zerenthis.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- KEEP YOUR EXISTING IMPORTS BELOW ----
from self_improver.outcome_engine import log_result, suggest_next_move

# ---- KEEP YOUR EXISTING ROUTES BELOW ----
@app.get("/health")
def health():
    return {"ok": True}

