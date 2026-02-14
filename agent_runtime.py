from config import MAX_ITERATIONS, CONFIDENCE_THRESHOLD
from skills.strategic import run_strategic_skill
import sys

class StrategicAgent:

    def __init__(self):
        self.conversation = []
        self.iteration_count = 0

    def start(self, initial_question: str):
        self.conversation = [
            {"role": "user", "content": initial_question}
        ]
        self.iteration_count = 0
        return self._iterate()

    def continue_session(self, user_answer: str):
        self.conversation.append({
            "role": "user",
            "content": user_answer
        })
        return self._iterate()

    def _iterate(self):
        if self.iteration_count >= MAX_ITERATIONS:
            return {
                "mode": "final_answer",
                "content": "Maximum iterations reached. Providing best recommendation based on available information.",
                "confidence": 0.7
            }

        result = run_strategic_skill(self.conversation)
        self.iteration_count += 1

        if result.mode == "final_answer":
            print(f"Result 1: {result}")
            return result

        if result.confidence >= CONFIDENCE_THRESHOLD:
            print(f"Result 2: {result}")
            return result

        # Save the agent's question before returning it
        self.conversation.append({
            "role": "assistant",
            "content": result.content
        })

        print(f"Result 3: {result}")
        return result
