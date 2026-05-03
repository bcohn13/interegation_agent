# Strategic Interrogation Agent
### Exploring AI Agents as an Engineering Practice

---

## About Me

- Actively exploring **AI Agents** as a technology area
- Interest: how LLMs can do more than answer questions — they can **reason iteratively**, ask clarifying questions, and drive toward a decision
- This project is my hands-on exploration of that idea

---

## What Problem Does This Solve?

> CEOs and founders facing complex decisions often get either **vague AI answers** or **information overload**.

They need something different:
- Asks the **right question** to cut through ambiguity
- Waits until it has **enough context** before giving advice
- Delivers one **clear, actionable recommendation**

---

## What Is an AI Agent?

A standard LLM call looks like this:

```
User → Prompt → LLM → Answer
```

An **AI Agent** is different — it has a **loop**:

```
User → Agent → Think → Is confidence high enough?
                  ↓ No              ↓ Yes
             Ask question     Give final answer
                  ↑
             User answers
```

The agent **decides its own next action** based on its current state.  
That's the key distinction from a simple chatbot.

---

## Project Architecture

```
main.py              ← FastAPI web server (entry point)
agent_runtime.py     ← Agent loop logic (iterate, decide, stop)
skills/strategic.py  ← Skill: calls GPT-4o with the strategic prompt
models.py            ← Pydantic schema for structured output
config.py            ← Model config and hyperparameters
```

### Request flow

```
POST /start  {"question": "..."}
        ↓
StrategicAgent.start()
        ↓
_iterate() → run_strategic_skill(conversation)
        ↓
GPT-4o returns JSON: { mode, content, confidence }
        ↓
mode == "question"?  → return question to user
mode == "final_answer" OR confidence >= 0.9?  → return answer
```

---

## The Agent Loop

```python
def _iterate(self) -> StrategicOutput:
    if self.iteration_count >= MAX_ITERATIONS:
        return StrategicOutput(mode="final_answer", ...)

    result = run_strategic_skill(self.conversation)
    self.iteration_count += 1

    if result.mode == "final_answer" or result.confidence >= CONFIDENCE_THRESHOLD:
        return result  # Done

    # Still uncertain — store the question and wait for user
    self.conversation.append({"role": "assistant", "content": result.content})
    return result
```

Key design decisions:
- **Confidence threshold** (0.9) — model self-reports when it's ready to answer
- **Max iterations** (6) — prevents infinite loops
- **Conversation history** — full context is carried forward on every call

---

## Structured Output with Pydantic

The model is instructed to always return valid JSON:

```json
{
  "mode": "question",
  "content": "What is the target market for this product?",
  "confidence": 0.7
}
```

Parsed and validated by Pydantic:

```python
class StrategicOutput(BaseModel):
    mode: Literal["question", "final_answer"]
    content: str
    confidence: float
```

This enforces a **contract** between the LLM and the application — a key pattern in production agent systems.

---

## Prompt Engineering

The system prompt is the "brain" of the agent. Key techniques used:

| Technique | What it does |
|---|---|
| Role definition | "You are a senior strategic advisor to a CEO..." |
| Conditional behaviour | Different instructions below/above confidence threshold |
| Output format enforcement | Strict JSON schema with examples of valid AND invalid outputs |
| Single-question constraint | Forces focused, high-leverage questions instead of a list |

---

## API Design

Two endpoints model the conversation turn-by-turn:

| Endpoint | Purpose |
|---|---|
| `POST /start` | Begin a new session with an initial question |
| `POST /continue` | Send the user's answer to the agent's last question |

Example interaction:

```
POST /start  { "question": "We're growing fast but execution is chaotic. Help." }
→ { "mode": "question", "content": "Is the chaos in hiring, delivery, or both?", "confidence": 0.6 }

POST /continue  { "answer": "Mainly hiring — we can't scale the team fast enough." }
→ { "mode": "final_answer", "content": "Appoint a Head of Talent this week...", "confidence": 0.92 }
```

---

## Error Handling

Production-grade handling for OpenAI failure modes:

```python
except RateLimitError:    → HTTP 503 "Quota exceeded"
except AuthenticationError: → HTTP 503 "Check API key"
except APIConnectionError:  → HTTP 503 "Connection failed"
except OpenAIError:         → HTTP 503 "Request failed"
```

The API never crashes silently — callers always get a meaningful status code and message.

---

## What I Learned / What This Demonstrates

| Area | Insight |
|---|---|
| **Agentic loops** | LLMs can be orchestrated to decide their own next step |
| **Confidence as a signal** | Self-reported confidence is a surprisingly effective stopping criterion |
| **Structured output** | Enforcing JSON via prompt + Pydantic is the practical pattern for agent systems |
| **Prompt engineering** | The system prompt IS the agent's behaviour — precision matters |
| **API design for agents** | Stateful, multi-turn interactions require different endpoint design than stateless APIs |

---

## What I Would Add Next

- **RAG** — inject relevant business context from documents before each model call
- **Persistent sessions** — store conversation history per user in a database
- **Streaming** — stream the model response token-by-token for better UX
- **Memory** — let the agent recall facts from past sessions
- **Evaluation** — measure answer quality and confidence calibration over time

---

## Summary

> This project is a deliberate exploration of **AI Agents as a software pattern** — not just calling an LLM, but building a loop that reasons, asks questions, and decides when it knows enough to act.

The architecture is intentionally small and readable so every design decision is visible.

**Stack:** Python · FastAPI · OpenAI GPT-4o · Pydantic · Uvicorn
