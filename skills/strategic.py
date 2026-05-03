import json
from config import client, MODEL, CONFIDENCE_THRESHOLD, RAG_ENABLED, RAG_TOP_K
from models import StrategicOutput
import re
from typing import cast
from openai import RateLimitError, AuthenticationError, APIConnectionError, APITimeoutError, OpenAIError
from openai.types.chat import ChatCompletionMessageParam
from rag import rag_store



SYSTEM_PROMPT = f"""
You are a senior strategic advisor to a CEO who values concise, actionable insights and does not have time to read long or vague answers.
 
Your responsibilities:
1. The user will ask you a business-related question. Analyze the question carefully.
2. If clarity is insufficient:
   - Ask exactly ONE high-leverage clarifying question at a time.
   - Focus on the question that most reduces decision uncertainty.
   - Avoid providing recommendations prematurely.
3. When confidence is above {CONFIDENCE_THRESHOLD}:
   - Provide a clear, concrete, and concise answer in one sentence.
   - Include one immediate next action the CEO can take.
   - Never respond with a question.
4. When confidence is below {CONFIDENCE_THRESHOLD}:
   - Provide a question to gain more clarity.
 
Output format:
- Always return a valid JSON object with the following structure:
  {{
    "mode": "question" or "final_answer",
    "content": "string",
    "confidence": float (0.0 to 1.0)
  }}
 
Guidelines:
- Use "mode": "question" when asking clarifying questions.
- Use "mode": "final_answer" only when confident in your response.
- Ensure "confidence" reflects the certainty of your response (e.g., 0.8 for high confidence).
- Avoid long explanations, irrelevant details, or multiple questions in a single response.
- Every answer should begin with "{{" and end with "}}".
- If the confidence is above {CONFIDENCE_THRESHOLD}, never return a question.

Examples of valid outputs:
1. Clarifying question:
   {{
     "mode": "question",
     "content": "What is the target market for this product?",
     "confidence": 0.7
   }}
2. Final answer:
   {{
     "mode": "final_answer",
     "content": "Focus on expanding into the European market immediately.",
     "confidence": 0.9
   }}

Examples of invalid outputs:
```json
{{
  "mode": "question",
  "content": "Is the employee's bad attitude affecting team performance or customer relations?",
  "confidence": 0.8
}}
```
"""

def run_strategic_skill(conversation: list[dict[str, str]]) -> StrategicOutput:
    # print("CONVERS")

    # try:
    #     confidence_score = conversation[-1]["confidence"]
    # except:
    #     confidence_score = INITIAL_CONFIDENCE

    latest_user_input = ""
    for message in reversed(conversation):
      if message.get("role") == "user":
        latest_user_input = message.get("content", "")
        break

    rag_context = ""
    if RAG_ENABLED and latest_user_input:
      retrieved_chunks = rag_store.retrieve(latest_user_input, top_k=RAG_TOP_K)
      if retrieved_chunks:
        context_lines = [
          f"- [{chunk['source']}#{chunk['chunk_id']}] {chunk['text']}"
          for chunk in retrieved_chunks
        ]
        rag_context = (
          "Use the retrieved business context below only when it is relevant. "
          "If it conflicts with user-provided facts, trust the user and ask one clarifying question.\n\n"
          "Retrieved context:\n"
          + "\n".join(context_lines)
        )

    effective_system_prompt = SYSTEM_PROMPT
    if rag_context:
      effective_system_prompt = f"{SYSTEM_PROMPT}\n\n{rag_context}"

    messages = cast(
        list[ChatCompletionMessageParam],
        [
        {"role": "system", "content": effective_system_prompt},
            *conversation,
        ],
    )

    try:
      response = client.chat.completions.create(
        model=MODEL,
        temperature=0.3,
        messages=messages,
      )
    except RateLimitError as e:
      raise RuntimeError(
        "OpenAI quota exceeded. Add billing/credits, then retry."
      ) from e
    except AuthenticationError as e:
      raise RuntimeError(
        "OpenAI authentication failed. Check OPENAI_API_KEY in this terminal session."
      ) from e
    except (APIConnectionError, APITimeoutError) as e:
      raise RuntimeError(
        "OpenAI connection failed or timed out. Check network and retry."
      ) from e
    except OpenAIError as e:
      raise RuntimeError(f"OpenAI request failed: {e}") from e

    content = response.choices[0].message.content
    if content is None:
      raise RuntimeError("Model returned an empty response.")

    # TODO: find permanent solution for returning valid json in every response
    # cleaned = re.sub(r'^```(?:json)?\s*|\s*```$', '', content.strip(), flags=re.MULTILINE)

    # Strip markdown code fences if the model wraps the JSON in ```json ... ```
    cleaned = re.sub(r'^```(?:json)?\s*|\s*```$', '', content.strip(), flags=re.MULTILINE)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model returned invalid JSON: {e}\nRaw content: {content}")

    # print("PARSED CONTENT: ", parsed.get("content"))

    # if not str(parsed.get("content", "")).endswith("?"):
    #     print("DEBUG SYSTEM PROMPT.")
    #     pdb.set_trace()


    return StrategicOutput(**parsed)
