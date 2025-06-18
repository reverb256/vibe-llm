# Vibe-LLM: AI Code Router

## Overview
Vibe-LLM is a modular, GPU-accelerated AI inference server and code router. It dynamically selects the best LLM or tool for coding tasks, enhances prompts with RAG (Retrieval Augmented Generation), and integrates with IDEs like VS Code (Continue.dev) or VOID IDE.

## Features (MVP)
- **Smart Model Routing**: Dynamically chooses the best LLM based on task type, latency, accuracy, and cost
- **Task Classifier**: Lightweight classifier to identify code generation, debugging, refactoring, etc.
- **RAG Integration**: Uses ChromaDB or Faiss for local vector search, plus optional web search
- **Tool Coordination (MCP)**: Integrates with Context7 and custom tools for web search, shell, and file access
- **OpenAI-Compatible API**: Drop-in replacement for OpenAI endpoints
- **IDE Integration**: Works with Continue.dev and VOID IDE out of the box
- **FOSS & Local First**: Supports open source models (Ollama, vLLM), local deployment, and easy customization

## Quick Start
1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/vibe-llm.git
   cd vibe-llm
   ```
2. **Set up Python environment**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. **Configure environment and models**
   - Copy `.env.example` to `.env` and fill in your secrets (HuggingFace, IO, etc.)
   - Edit `config.yaml` to define your models, RAG, and tools
4. **Run the server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
5. **Test endpoints**
   - `POST /api/generate` — Smart router endpoint (recommended)
   - `POST /v1/chat/completions` — OpenAI-compatible chat
   - `GET /v1/models` — List all available models
   - `GET /v1/agents` — List all available agents

## API Reference
### `/api/generate` (recommended)
- **POST** JSON: `{ "prompt": "...", "tags": ["code"], "rag": true }`
- Returns: `{ "model": "...", "task": "...", "response": "..." }`

### OpenAI-Compatible Endpoints
- `POST /v1/chat/completions`
- `POST /v1/completions`

## RAG & Tool Coordination
- **RAG endpoints**: `/api/rag/add`, `/api/rag/query` for document ingestion and retrieval
- **Tool endpoints**: `/api/tool/shell`, `/api/tool/read_file`, `/api/tool/write_file` for MCP/Context7 integration
- **CLI tool**: `vibe-cli.py` for standalone prompt testing

## Example Usage
### Add docs to RAG
```bash
curl -X POST http://localhost:8000/api/rag/add -H 'Content-Type: application/json' -d '{"docs": ["FastAPI is a Python web framework.", "Paris is the capital of France."]}'
```
### Query RAG
```bash
curl -X POST http://localhost:8000/api/rag/query -H 'Content-Type: application/json' -d '{"query": "What is the capital of France?"}'
```
### Run shell command
```bash
curl -X POST http://localhost:8000/api/tool/shell -H 'Content-Type: application/json' -d '{"command": "ls -l"}'
```
### CLI tool
```bash
python vibe-cli.py "Generate a Python function to add two numbers."
```

## Configuration
- **.env**: Secrets for HuggingFace, IO, etc.
- **config.yaml**: Models, RAG, and tool settings

## IDE Integration
- See [Continue.dev](https://continue.dev/) or VOID IDE docs
- Point your IDE to `http://localhost:8000/api/generate` for smart routing

## Extensibility
- Add new models/tools in `config.yaml`
- Extend backends in `app/`
- Plugin system coming soon

## Contributing
- Fork, branch, and submit PRs for new features or bug fixes
- Document all new endpoints, models, and agents
- Add/Update tests for all new features

## License
MIT License

## References
- [FastAPI](https://fastapi.tiangolo.com/)
- [vLLM](https://vllm.ai/)
- [HuggingFace Hub](https://huggingface.co/docs/hub/index)
- [ChromaDB](https://www.trychroma.com/)
- [Continue.dev](https://continue.dev/)
