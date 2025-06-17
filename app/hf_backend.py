import os
import logging
from huggingface_hub import InferenceClient, list_models, model_info

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

class HuggingFaceBackend:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = InferenceClient(model=model_name, token=HUGGINGFACE_TOKEN)
        self.info = None
        try:
            self.info = model_info(model_name)
        except Exception as e:
            logging.warning(f"Could not fetch model info for {model_name}: {e}")

    def get_supported_tasks(self):
        if self.info and hasattr(self.info, 'pipeline_tag'):
            return [self.info.pipeline_tag]
        if self.info and hasattr(self.info, 'library_name') and self.info.library_name:
            return [self.info.library_name]
        return []

    def chat(self, prompt: str, max_new_tokens: int = 128, temperature: float = 0.7):
        # Try to auto-detect the correct inference method
        tasks = self.get_supported_tasks()
        try:
            if "text-generation" in tasks:
                response = self.client.text_generation(
                    prompt,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=True,
                    return_full_text=False
                )
                return response
            elif "conversational" in tasks or "conversation" in tasks:
                response = self.client.conversational(
                    prompt,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature
                )
                return response
            else:
                return f"[HuggingFace Error] Model {self.model_name} does not support text-generation or conversational tasks. Supported: {tasks}"
        except Exception as e:
            logging.error(f"HuggingFace inference error: {e}")
            return f"[HuggingFace Error] {e}"

    @staticmethod
    def list_text_generation_models(limit=20):
        # List public models that support text-generation or conversational
        models = list_models(limit=limit)
        filtered = []
        for m in models:
            if hasattr(m, 'pipeline_tag') and m.pipeline_tag in ("text-generation", "conversational", "conversation"):
                filtered.append(m.modelId)
        return filtered
