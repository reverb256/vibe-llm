# vibe-llm: Local AI Inference Server

This project provides a local AI inference server with the following features:
- **OpenAI-compatible API** (for Ollama, Open WebUI, IDEs, etc.)
- **vLLM** for fast local inference with GPU (NVIDIA 3090 via CUDA)
- **HuggingFace Hub** integration for remote models
- **IO Intelligence** integration for cloud models
- **RAG (Retrieval-Augmented Generation)** support (using FAISS or ChromaDB)
- **Network-accessible**: Bind to 0.0.0.0 for LAN access

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set your API keys in a `.env` file:
   ```env
   HUGGINGFACE_TOKEN=your_hf_token
   IOINTEL_TOKEN=your_iointel_token
   ```
3. Run the server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## Features
- OpenAI-compatible endpoints: `/v1/chat/completions`, etc.
- Model routing: local (vLLM), HuggingFace, or IO Intelligence
- RAG pipeline for document-augmented answers

## Requirements
- Python 3.10+
- CUDA-enabled GPU (for vLLM)

## TODO
- Implement vLLM backend
- Implement HuggingFace backend
- Implement IO Intelligence backend
- Implement RAG pipeline
- Add authentication and rate limiting

## Docker Usage

### Build and Run with Docker Compose

1. Build the image and start the service (with GPU support):
   ```bash
   docker compose up --build
   ```
   The API will be available at http://localhost:8000

2. To stop the service:
   ```bash
   docker compose down
   ```

> **Note:**
> - Requires Docker with NVIDIA Container Toolkit for GPU access.
> - Your `.env` file is automatically used for API keys.

---

This project is in active development. Contributions welcome!
