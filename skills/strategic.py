import json
from config import client, MODEL
from models import StrategicOutput

SYSTEM_PROMPT = """
You are a senior strategic advisor.

Your task:
- Ask exactly ONE high-leverage clarifying question at a time.
- Only ask the question that most reduces decision uncertainty.
- Do NOT provide recommendations prematurely.
- When enough clarity exists, switch to final_answer mode.

When giving final_answer:
- Provide a clear, concrete recommendation.
- Briefly explain reasoning.
- Include one immediate next action.

Always return valid JSON:

{
  "mode": "question" or "final_answer",
  "content": "string",
  "confidence": 0.0-1.0
}
"""

def run_strategic_skill(conversation):
    #print(conversation)
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *conversation
        ],
    )
    for choice in response.choices:
        print(choice)
    #print(response.choices.message)
    content = response.choices[0].message.content
    #print(f"Content: {content}")
    try:
        parsed = json.loads(content)
    except:
        parsed={"content": content}
    

    return StrategicOutput(**parsed)
