from pydantic import BaseModel
from typing import Literal

class StrategicOutput(BaseModel):
    mode: Literal["question", "final_answer"]
    content: str
    confidence: float
