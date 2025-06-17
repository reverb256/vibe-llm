from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from .hf_backend import HuggingFaceBackend
from .iointel_backend import IOIntelligenceBackend

load_dotenv()

app = FastAPI(title="vibe-llm: Local AI Inference Server")

@app.get("/")
def root():
    return {"message": "vibe-llm API is running."}

# OpenAI-compatible endpoint stub
@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    model = body.get("model", "gpt2")
    messages = body.get("messages", [])
    prompt = messages[-1]["content"] if messages else ""
    # Routing logic: use IO Intelligence if model name starts with 'meta-llama/' or other IOIntel models
    if model.startswith("meta-llama/") or model.startswith("deepseek-ai/") or model.startswith("Qwen/"):
        io_backend = IOIntelligenceBackend(model)
        response = io_backend.chat(messages)
        return JSONResponse({"choices": [{"message": {"role": "assistant", "content": response}}]})
    # Otherwise, use HuggingFace backend
    hf = HuggingFaceBackend(model)
    response = hf.chat(prompt)
    return JSONResponse({"choices": [{"message": {"role": "assistant", "content": response}}]})
