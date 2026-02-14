from openai import OpenAI
import os

# Ensure you set your OPENAI_API_KEY in your environment
client = OpenAI(api_key=os.getenv("Open_AI_Key"))

MODEL = "gpt-4o"
MAX_ITERATIONS = 6
CONFIDENCE_THRESHOLD = 0.8
