from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/command", tags=["command_center"])

class CommandRequest(BaseModel):
    prompt: str

def fake_intelligence(prompt: str):
    return {
        "title": f"Generated Asset for: {prompt}",
        "summary": f"This is a high-converting asset based on: {prompt}",
        "content": f"""TITLE: {prompt}

This is a premium generated content piece designed to convert.

- Hook: Powerful opening
- Value: Clear transformation
- CTA: Action-driving close

Use this as a sellable asset, post, or product."""
    }

@router.post("/run")
def run_command(req: CommandRequest):
    job_id = uuid.uuid4().hex
    result = fake_intelligence(req.prompt)

    return {
        "status": "completed",
        "job_id": job_id,
        "created_at": datetime.utcnow().isoformat(),
        "result": {
            "title": result["title"],
            "summary": result["summary"],
            "content": result["content"]
        }
    }
