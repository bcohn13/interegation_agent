from fastapi import FastAPI
from pydantic import BaseModel
from agent_runtime import StrategicAgent

app = FastAPI()
agent = StrategicAgent()

class StartRequest(BaseModel):
    question: str

class ContinueRequest(BaseModel):
    answer: str

@app.post("/start")
def start_session(request: StartRequest):
    return agent.start(request.question)

@app.post("/continue")
def continue_session(request: ContinueRequest):
    return agent.continue_session(request.answer)
