from openai import OpenAI
import os

# Ensure you set your OPENAI_API_KEY in your environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"
MAX_ITERATIONS = 6
CONFIDENCE_THRESHOLD = 0.85
