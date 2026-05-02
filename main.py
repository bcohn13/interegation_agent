# Entry point for the Strategic Interrogation Agent API.
# Exposes two HTTP endpoints:
#   POST /start   — kick off a new session with the user's initial question
#   POST /continue — send the user's answer to the agent's follow-up question
#
# The agent runs an iterative loop: it either asks a clarifying question or
# returns a final answer once its confidence crosses CONFIDENCE_THRESHOLD
# (or MAX_ITERATIONS is reached).

from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from agent_runtime import StrategicAgent

app = FastAPI()

# Single shared agent instance — holds the conversation history across requests
agent = StrategicAgent()


# --- Request schemas ---

class StartRequest(BaseModel):
    question: str  # The user's opening question/topic to investigate

class ContinueRequest(BaseModel):
    answer: str  # The user's reply to the agent's last follow-up question


# --- Endpoints ---

@app.post("/start")
def start_session(request: StartRequest):
    """Start a new interrogation session with an initial question.
    
    Resets conversation history and runs the first agent iteration.
    Returns either a follow-up question (mode='question') or a final
    answer (mode='final_answer') if confidence is already high enough.
    """
    try:
        return agent.start(request.question)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {e}") from e


@app.post("/continue")
def continue_session(request: ContinueRequest):
    """Continue an existing session by supplying the user's answer.
    
    Appends the answer to the conversation history and runs the next
    agent iteration. Repeats until the agent reaches sufficient confidence
    or hits the maximum iteration limit.
    """
    try:
        return agent.continue_session(request.answer)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {e}") from e
