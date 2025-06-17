import os
import openai

IOINTEL_TOKEN = os.getenv("IOINTEL_TOKEN")

class IOIntelligenceBackend:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = openai.OpenAI(
            api_key=IOINTEL_TOKEN,
            base_url="https://api.intelligence.io.solutions/api/v1/",
        )

    def chat(self, messages, max_tokens=128, temperature=0.7):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            stream=False
        )
        return response.choices[0].message.content
