from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from .registry import ModelRegistry
from .iointel_backend import IOIntelligenceBackend
from .vllm_backend import VLLMBackend

load_dotenv()

app = FastAPI(title="vibe-llm: Local AI Inference Server")

# Initialize registry and discover IO models/agents at startup
ioregistry = ModelRegistry()
ioregistry.models = ioregistry._discover_io_models()
ioregistry.agents = ioregistry._discover_io_agents()

@app.get("/")
def root():
    return {"message": "vibe-llm API is running."}

# OpenAI-compatible endpoint stub
@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    model = body.get("model")
    messages = body.get("messages", [])
    if not model:
        return JSONResponse({"error": "Model must be specified."}, status_code=400)
    # Use IO Intelligence backend for all models
    io_backend = IOIntelligenceBackend(model)
    try:
        response = io_backend.chat(messages)
        return JSONResponse({"choices": [{"message": {"role": "assistant", "content": response}}]})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/v1/models")
async def list_models():
    # Only IO models for now
    return {"models": [m["id"] for m in ioregistry.models]}

@app.get("/v1/agents")
async def list_io_agents():
    return {"agents": ioregistry.agents}
