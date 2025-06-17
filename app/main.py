from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="vibe-llm: Local AI Inference Server")

@app.get("/")
def root():
    return {"message": "vibe-llm API is running."}

# OpenAI-compatible endpoint stub
@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    # TODO: Route to vLLM, HuggingFace, or IO Intelligence based on model
    return JSONResponse({"choices": [{"message": {"role": "assistant", "content": "[Stub]"}}]})
