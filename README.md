# Vibe-LLM: Enterprise-Grade Local AI Inference Server

## Overview
Vibe-LLM is a modular, GPU-accelerated AI inference server with OpenAI-compatible endpoints. It supports:
- Local vLLM backend (GPU inference)
- HuggingFace (remote, with dynamic task support)
- IO Intelligence (remote/agent)
- RAG (Retrieval-Augmented Generation) and Knowledge Graph integration
- Secure proxying of all external requests via vLLM
- Auto-discovery and unified registry of all models and agents
- Smart routing and graceful fallback

## Features
- **OpenAI-compatible API**: Drop-in replacement for OpenAI endpoints
- **Unified Model/Agent Registry**: Auto-discovers and merges models/agents from all providers
- **Smart Routing**: Selects the best model for each request, with fallback
- **Enterprise Security**: All external calls are proxied and sanitized
- **RAG & Knowledge Graph**: Integrates with advanced RAG MCP servers and Neo4j for code validation and hallucination detection
- **Extensible**: Easily add new providers, tasks, or RAG strategies

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
3. **Configure environment variables**
   - Copy `.env.example` to `.env` and fill in your secrets (HuggingFace, IO, RAG, etc.)
4. **Run the server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
5. **Test endpoints**
   - `GET /v1/models` — List all available models
   - `GET /v1/agents` — List all available agents
   - `POST /v1/chat/completions` — OpenAI-compatible chat

## RAG & Knowledge Graph Integration
- Integrate with [mcp-crawl4ai-rag](https://github.com/coleam00/mcp-crawl4ai-rag) for advanced RAG and code validation.
- See `BEST_PRACTICES.md` for recommended RAG strategies and knowledge graph setup.

## Best Practices
- See [BEST_PRACTICES.md](./BEST_PRACTICES.md) for architecture, security, and collaboration guidelines.

## Contributing
- Fork, branch, and submit PRs for new features or bug fixes.
- Document all new endpoints, models, and agents.
- Add/Update tests for all new features.

## License
MIT License

## References
- [FastAPI](https://fastapi.tiangolo.com/)
- [vLLM](https://vllm.ai/)
- [HuggingFace Hub](https://huggingface.co/docs/hub/index)
- [Crawl4AI RAG MCP](https://github.com/coleam00/mcp-crawl4ai-rag)
- [Neo4j](https://neo4j.com/)
