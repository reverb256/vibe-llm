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
from .tool_registry import ToolRegistry
from .usage_tracker import UsageTracker
from .orchestrator import Orchestrator
from .telemetry import Telemetry
from .sanitize import sanitize_input
from .auth import get_current_client, get_admin_client, check_permission
from fastapi import Depends
import yaml

load_dotenv()

app = FastAPI(title="vibe-llm: Local AI Inference Server")

# Default models for different use cases
DEFAULT_CHAT_MODEL = "io:meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
DEFAULT_CONTENT_MODEL = "io:meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"

# Initialize registry and discover IO models/agents at startup
ioregistry = ModelRegistry()
ioregistry.models = ioregistry._discover_io_models()
ioregistry.agents = ioregistry._discover_io_agents()

# Initialize usage tracker
usage_tracker = UsageTracker()
telemetry = Telemetry()

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

def get_backend(model: str, provider: str = None, rag_corpus=None, allow_rotation=True):
    """
    Select backend based on model/provider naming convention or explicit provider.
    If usage limit is hit, rotate to next available model for the task.
    """
    if provider == 'io' or (model and model.startswith('io:')):
        if usage_tracker.is_limited(model):
            # Rotate to next available IO model
            from .model_selector import ModelSelector
            selector = ModelSelector()
            next_model = selector.select('chat', tags=['io'])
            if next_model != model:
                model = next_model
        usage_tracker.increment(model)
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

@app.get("/api/tools")
async def list_tools():
    registry = ToolRegistry()
    return {"tools": registry.list_tools()}

@app.post("/api/tools/run")
async def run_tool(request: Request):
    body = await request.json()
    name = body.get("name")
    args = body.get("args", [])
    kwargs = body.get("kwargs", {})
    registry = ToolRegistry()
    result = registry.run_tool(name, *args, **kwargs)
    return result

@app.post("/api/orchestrate")
async def api_orchestrate(request: Request):
    body = await request.json()
    task = body.get("task")
    steps = body.get("steps", [])
    if not task or not steps:
        return JSONResponse({"error": "task and steps must be specified"}, status_code=400)
    from .model_selector import ModelSelector
    from .tool_registry import ToolRegistry
    orchestrator = Orchestrator(ModelSelector(), ToolRegistry())
    # Sanitize all step args/kwargs
    for step in steps:
        if 'args' in step:
            step['args'] = [sanitize_input(str(a)) for a in step['args']]
        if 'kwargs' in step:
            step['kwargs'] = {k: sanitize_input(str(v)) for k, v in step['kwargs'].items()}
    results = orchestrator.orchestrate(task, steps)
    telemetry.log('orchestrate', {'task': task, 'steps': steps, 'results': results})
    return {"results": results}

@app.get("/api/telemetry")
async def api_telemetry():
    return telemetry.get_metrics()

# Client-specific endpoints for business applications

@app.post("/v1/admin/parse-command")
async def parse_admin_command(request: Request, client: dict = Depends(get_admin_client)):
    """Parse natural language admin commands for content management systems"""
    body = await request.json()
    command = body.get("command")
    context = body.get("context", "business_website")
    
    if not command:
        return JSONResponse({"error": "command must be specified"}, status_code=400)
    
    # Sanitize input
    command = sanitize_input(command)
    
    # Use AI to parse the command
    backend = get_backend(DEFAULT_CHAT_MODEL)
    
    prompt = f"""Parse this admin command for a {context}:

Command: "{command}"

Extract:
1. target (what section/component to modify: hero, services, contact, about, etc.)
2. action (what to do: update_text, update_contact, add_section, etc.)
3. parameters (specific details like content, field, value)

Return as JSON:
{{"target": "...", "action": "...", "parameters": {{...}}}}"""

    try:
        response = backend.chat([{"role": "user", "content": prompt}], max_tokens=256, temperature=0.1)
        # Parse the JSON response
        import json
        parsed = json.loads(response.strip())
        
        telemetry.log('admin_command_parse', {'command': command, 'context': context, 'parsed': parsed})
        return {"parsed_command": parsed, "success": True}
    except Exception as e:
        return JSONResponse({"error": f"Failed to parse command: {str(e)}"}, status_code=500)

@app.post("/v1/business/chat")
async def business_chat(request: Request, client: dict = Depends(get_current_client)):
    """Chat endpoint tailored for business websites with context awareness"""
    body = await request.json()
    message = body.get("message")
    business_type = body.get("business_type", "service")
    business_context = body.get("business_context", {})
    session_id = body.get("session_id")
    
    if not message:
        return JSONResponse({"error": "message must be specified"}, status_code=400)
    
    # Sanitize input
    message = sanitize_input(message)
    
    # Build context-aware prompt
    context_prompt = f"""You are a helpful assistant for a {business_type} business website. 

Business Context:
- Type: {business_type}
- Services: {business_context.get('services', 'Professional services')}
- Location: {business_context.get('location', 'Local area')}
- Key Features: {business_context.get('features', 'Quality service')}

User Message: {message}

Respond helpfully and professionally, staying in character for this business."""

    backend = get_backend(DEFAULT_CHAT_MODEL)
    
    try:
        response = backend.chat([{"role": "user", "content": context_prompt}], max_tokens=512, temperature=0.7)
        
        telemetry.log('business_chat', {
            'business_type': business_type, 
            'session_id': session_id,
            'message_length': len(message)
        })
        
        return {
            "response": response,
            "session_id": session_id,
            "business_type": business_type,
            "success": True
        }
    except Exception as e:
        return JSONResponse({"error": f"Chat failed: {str(e)}"}, status_code=500)

@app.post("/v1/content/generate")
async def generate_content(request: Request, client: dict = Depends(get_current_client)):
    """Generate content for business websites"""
    body = await request.json()
    content_type = body.get("content_type")  # hero, service_description, testimonial, etc.
    business_info = body.get("business_info", {})
    requirements = body.get("requirements", "")
    
    if not content_type:
        return JSONResponse({"error": "content_type must be specified"}, status_code=400)
    
    prompt = f"""Generate {content_type} content for a business website.

Business Information:
- Name: {business_info.get('name', 'Professional Services')}
- Industry: {business_info.get('industry', 'Service Industry')}
- Location: {business_info.get('location', 'Local')}
- Key Services: {business_info.get('services', 'Professional services')}

Requirements: {requirements}

Generate professional, engaging content that converts visitors into customers."""

    backend = get_backend(DEFAULT_CONTENT_MODEL)
    
    try:
        content = backend.chat([{"role": "user", "content": prompt}], max_tokens=1024, temperature=0.8)
        
        telemetry.log('content_generation', {
            'content_type': content_type,
            'business_name': business_info.get('name', 'unknown')
        })
        
        return {
            "content": content,
            "content_type": content_type,
            "success": True
        }
    except Exception as e:
        return JSONResponse({"error": f"Content generation failed: {str(e)}"}, status_code=500)

@app.post("/v1/consciousness/metrics")
async def consciousness_metrics(request: Request):
    """Track consciousness metrics for the federation"""
    body = await request.json()
    agent_id = body.get("agent_id")
    metrics = body.get("metrics", {})
    
    if not agent_id:
        return JSONResponse({"error": "agent_id must be specified"}, status_code=400)
    
    # Store metrics in telemetry
    telemetry.log('consciousness_metrics', {
        'agent_id': agent_id,
        'metrics': metrics,
        'timestamp': telemetry.current_time()
    })
    
    return {"success": True, "agent_id": agent_id}
