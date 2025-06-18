from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from .registry import ModelRegistry
from .iointel_backend import IOIntelligenceBackend
from .vllm_backend import VLLMBackend
from .hf_backend import HuggingFaceBackend
from .rag_backend import RAGBackend
from .task_classifier import TaskClassifier
from .model_selector import ModelSelector
from .chroma_rag import ChromaRAG
from .tool_coordinator import ToolCoordinator
import yaml

load_dotenv()

app = FastAPI(title="vibe-llm: Local AI Inference Server")

# Initialize registry and discover IO models/agents at startup
ioregistry = ModelRegistry()
ioregistry.models = ioregistry._discover_io_models()
ioregistry.agents = ioregistry._discover_io_agents()

@app.get("/")
def root():
    return {"message": "vibe-llm API is running."}

# Backend selection logic
BACKEND_MAP = {
    'io': IOIntelligenceBackend,
    'vllm': VLLMBackend,
    'hf': HuggingFaceBackend,
    'rag': RAGBackend,
}

def get_backend(model: str, provider: str = None, rag_corpus=None):
    """
    Select backend based on model/provider naming convention or explicit provider.
    """
    if provider == 'io' or (model and model.startswith('io:')):
        return IOIntelligenceBackend(model.replace('io:', ''))
    elif provider == 'vllm' or (model and model.startswith('vllm:')):
        return VLLMBackend(model.replace('vllm:', ''))
    elif provider == 'hf' or (model and model.startswith('hf:')):
        return HuggingFaceBackend(model.replace('hf:', ''))
    elif provider == 'rag' or (model and model.startswith('rag:')):
        # For demo, use a static corpus
        corpus = rag_corpus or [
            "The capital of France is Paris.",
            "FastAPI is a modern Python web framework.",
            "vLLM enables fast LLM inference on GPUs.",
        ]
        return RAGBackend(model.replace('rag:', ''), corpus)
    else:
        # Default to IO Intelligence
        return IOIntelligenceBackend(model)

@app.post("/v1/completions")
async def completions(request: Request):
    body = await request.json()
    model = body.get("model")
    prompt = body.get("prompt")
    provider = body.get("provider")
    max_tokens = body.get("max_tokens", 128)
    temperature = body.get("temperature", 0.7)
    if not model or not prompt:
        return JSONResponse({"error": "Model and prompt must be specified."}, status_code=400)
    backend = get_backend(model, provider)
    try:
        # Use backend-specific logic
        if isinstance(backend, IOIntelligenceBackend):
            response = backend.chat([{"role": "user", "content": prompt}], max_tokens, temperature)
        elif isinstance(backend, VLLMBackend):
            response = backend.chat(prompt, max_tokens, temperature)
        elif isinstance(backend, HuggingFaceBackend):
            response = backend.chat(prompt, max_new_tokens=max_tokens, temperature=temperature)
        elif isinstance(backend, RAGBackend):
            response = backend.chat([{"role": "user", "content": prompt}], max_new_tokens=max_tokens, temperature=temperature)
        else:
            response = "[Error] Unknown backend type."
        return JSONResponse({"choices": [{"text": response}]})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    model = body.get("model")
    messages = body.get("messages", [])
    provider = body.get("provider")
    max_tokens = body.get("max_tokens", 128)
    temperature = body.get("temperature", 0.7)
    if not model:
        return JSONResponse({"error": "Model must be specified."}, status_code=400)
    backend = get_backend(model, provider)
    try:
        response = backend.chat(messages, max_tokens, temperature)
        return JSONResponse({"choices": [{"message": {"role": "assistant", "content": response}}]})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/v1/models")
async def list_models():
    # Unified model list from all providers
    ioregistry.discover_all()
    return {"models": [m["id"] for m in ioregistry.models]}

@app.get("/v1/agents")
async def list_io_agents():
    return {"agents": ioregistry.agents}

@app.get("/openai/verify")
@app.post("/openai/verify")
def openai_verify():
    return JSONResponse({"success": True})

@app.get("/openai/models")
def openai_models():
    ioregistry.discover_all()
    # Return models in OpenAI format for Open WebUI compatibility
    return {"data": [{"id": m["id"], "object": "model"} for m in ioregistry.models]}

@app.post("/api/generate")
async def api_generate(request: Request):
    body = await request.json()
    prompt = body.get("prompt")
    tags = body.get("tags", [])
    rag = body.get("rag", False)
    if not prompt:
        return JSONResponse({"error": "Prompt must be specified."}, status_code=400)
    classifier = TaskClassifier()
    task = classifier.classify(prompt)
    selector = ModelSelector()
    model_id = selector.select(task, tags)
    provider = model_id.split(":")[0] if model_id else None
    backend = get_backend(model_id, provider)
    try:
        if hasattr(backend, 'chat'):
            response = backend.chat([{"role": "user", "content": prompt}], 128, 0.7)
        else:
            response = backend.generate(prompt, 128, 0.7)
        return JSONResponse({
            "model": model_id,
            "task": task,
            "response": response
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/rag/add")
async def rag_add(request: Request):
    body = await request.json()
    docs = body.get("docs")
    if not docs or not isinstance(docs, list):
        return JSONResponse({"error": "docs must be a list of strings"}, status_code=400)
    rag = ChromaRAG()
    rag.add_documents(docs)
    return {"status": "added", "count": len(docs)}

@app.post("/api/rag/query")
async def rag_query(request: Request):
    body = await request.json()
    query = body.get("query")
    top_k = body.get("top_k", 3)
    if not query:
        return JSONResponse({"error": "query must be specified"}, status_code=400)
    rag = ChromaRAG()
    results = rag.query(query, top_k=top_k)
    return {"results": results}

@app.post("/api/tool/shell")
async def tool_shell(request: Request):
    body = await request.json()
    command = body.get("command")
    if not command:
        return JSONResponse({"error": "command must be specified"}, status_code=400)
    tools = ToolCoordinator()
    result = tools.run_shell(command)
    return result

@app.post("/api/tool/read_file")
async def tool_read_file(request: Request):
    body = await request.json()
    path = body.get("path")
    if not path:
        return JSONResponse({"error": "path must be specified"}, status_code=400)
    tools = ToolCoordinator()
    result = tools.read_file(path)
    return result

@app.post("/api/tool/write_file")
async def tool_write_file(request: Request):
    body = await request.json()
    path = body.get("path")
    content = body.get("content")
    if not path or content is None:
        return JSONResponse({"error": "path and content must be specified"}, status_code=400)
    tools = ToolCoordinator()
    result = tools.write_file(path, content)
    return result
