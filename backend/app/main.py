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
    text = q.lower()

    if "video idea" in text:
        return {"response": "YouTube Idea: 'I Let AI Run My Life for 24 Hours (Insane Results)'"}
    
    if "business" in text:
        return {"response": "Start a niche AI tool, post daily content, monetize with subscriptions."}

    return {"response": f"Zerenthis processed: {q}"}


# 🔥 FOUNDER ENDPOINT
@app.get("/founder")
def founder():
    return {
        "status": "Founder access confirmed",
        "tools": [
            "Content Generator",
            "YouTube Idea Engine",
            "Execution Planner",
            "Automation System (coming soon)"
        ]
    }