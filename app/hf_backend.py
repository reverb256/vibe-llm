import os
import logging
from huggingface_hub import InferenceClient, list_models, ModelFilter

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

class HuggingFaceBackend:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = InferenceClient(model=model_name, token=HUGGINGFACE_TOKEN)

    def chat(self, prompt: str, max_new_tokens: int = 128, temperature: float = 0.7):
        try:
            response = self.client.text_generation(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                return_full_text=False
            )
            return response
        except Exception as e:
            logging.error(f"HuggingFace inference error: {e}")
            return f"[HuggingFace Error] {e}"

    @staticmethod
    def list_text_generation_models(limit=20):
        # List public models that support text-generation
        models = list_models(filter=ModelFilter(task="text-generation"), limit=limit)
        return [m.modelId for m in models]
