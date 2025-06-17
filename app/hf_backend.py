import os
from huggingface_hub import InferenceClient

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

class HuggingFaceBackend:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = InferenceClient(model=model_name, token=HUGGINGFACE_TOKEN)

    def chat(self, prompt: str, max_new_tokens: int = 128, temperature: float = 0.7):
        response = self.client.text_generation(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
            return_full_text=False
        )
        return response
