from fastapi import FastAPI
from backend.app.routes.brain_patch import router as brain_router

app = FastAPI()
app.include_router(brain_router)
