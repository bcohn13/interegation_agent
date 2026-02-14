import json
from config import client, MODEL, INITIAL_CONFIDENCE, CONFIDENCE_THRESHOLD
from models import StrategicOutput
import re
import pdb



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

def run_strategic_skill(conversation):
    # print("CONVERS")

    # try:
    #     confidence_score = conversation[-1]["confidence"]
    # except:
    #     confidence_score = INITIAL_CONFIDENCE

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
    # cleaned = re.sub(r'^```(?:json)?\s*|\s*```$', '', content.strip(), flags=re.MULTILINE)

    try:
        parsed = json.loads(content)
        print("Content IS valid. Why does it work?")
        # pdb.set_trace()
    except:
        print("DEBUG content. Content needs to be a valid json string")
        pdb.set_trace()

    parsed_content = parsed["content"]
    # print("PARSED CONTENT: ", parsed_content)

    # if not parsed_content.endswith("?"):
    #     print("DEBUG SYSTEM PROMPT.")
    #     pdb.set_trace()


    return StrategicOutput(**parsed)
