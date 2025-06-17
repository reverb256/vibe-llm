import os
import openai
import requests

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

    @staticmethod
    def list_io_models():
        url = "https://api.intelligence.io.solutions/api/v1/models"
        headers = {"Authorization": f"Bearer {IOINTEL_TOKEN}"}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return [m["id"] for m in data.get("data", [])]
        except Exception as e:
            return [f"[IO Intelligence Error] {e}"]

    @staticmethod
    def list_io_agents():
        url = "https://api.intelligence.io.solutions/api/v1/agents"
        headers = {"Authorization": f"Bearer {IOINTEL_TOKEN}"}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            agents = data.get("agents", {})
            return [{"id": k, "name": v.get("name"), "description": v.get("description"), "tags": v.get("metadata", {}).get("tags", [])} for k, v in agents.items()]
        except Exception as e:
            return [{"error": f"[IO Intelligence Agent Error] {e}"}]
