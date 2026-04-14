from pydantic import BaseModel, Field

from typing import List, Optional



class Idea(BaseModel):

    idea: str

    score: int = Field(default=0, ge=0, le=100)



class ProductResult(BaseModel):

    title: str

    summary: str

    bullets: List[str]



class TrafficResult(BaseModel):

    hooks: List[str]

    captions: List[str]



class ExecutionResult(BaseModel):

    idea: str

    product: ProductResult

    traffic: TrafficResult

    status: str

    output_files: List[str] = []

    notes: Optional[str] = None









