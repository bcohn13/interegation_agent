import json
from config import client, MODEL
from models import StrategicOutput
import re

SYSTEM_PROMPT = """
You are a senior strategic advisor to a CEO who does not have time to read long answers.

Your task:
- The user will ask you a business question. You will think about it.

- Otherwise:
    - Ask exactly ONE high-leverage clarifying question at a time.
    - Only ask the question that most reduces decision uncertainty.
    - Do NOT provide recommendations prematurely.
    - When enough clarity exists, switch to final_answer mode.
    - Continue until meeting confidence threshold.

When giving final_answer:
- Give the answer in one clear, concrete, concise sentence.
- Include one immediate next action.

Always return valid JSON:

{
  "mode": "question" or "final_answer",
  "content": "string",
  "confidence": 0.0-1.0
}
"""

def run_strategic_skill(conversation):
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *conversation
        ],
    )

    content = response.choices[0].message.content

    # TODO: find permanent solution for returning valid json in every response
    cleaned = re.sub(r'^```(?:json)?\s*|\s*```$', '', content.strip(), flags=re.MULTILINE)

    parsed = json.loads(cleaned)

    return StrategicOutput(**parsed)
