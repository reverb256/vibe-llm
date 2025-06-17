import os
from vllm import LLM, SamplingParams

class VLLMBackend:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.llm = LLM(model=model_name, dtype="auto")

    def chat(self, prompt: str, max_tokens: int = 128, temperature: float = 0.7):
        sampling_params = SamplingParams(
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1.0,
            stop=None
        )
        outputs = self.llm.generate([prompt], sampling_params)
        return outputs[0].outputs[0].text.strip()
