"""
Unified Model & Agent Registry for vibe-llm
- Discovers and stores metadata for all available models and agents from all providers
- Provides unified query and selection interface
- Extensible for new providers and metadata fields
"""

from typing import List, Dict, Any
import logging
from .iointel_backend import IOIntelligenceBackend

class ModelRegistry:
    def __init__(self):
        self.models = []  # List of dicts: {id, provider, tasks, health, ...}
        self.agents = []  # List of dicts: {id, provider, description, ...}

    def discover_all(self):
        """Discover models and agents from all providers."""
        self.models = self._discover_io_models() + self._discover_hf_models()
        self.agents = self._discover_io_agents()

    def _discover_hf_models(self) -> List[Dict[str, Any]]:
        # TODO: Call HuggingFace backend, get models and metadata
        return []

    def _discover_io_models(self):
        model_ids = IOIntelligenceBackend.list_io_models()
        # Add metadata for each model
        return [{
            "id": m,
            "provider": "io",
            "tasks": ["chat", "text-generation"],  # Assume chat/text-generation for now
            "health": "unknown"
        } for m in model_ids if isinstance(m, str) and not m.startswith("[IO Intelligence Error]")]

    def _discover_io_agents(self):
        agents = IOIntelligenceBackend.list_io_agents()
        # Add provider field
        return [{**a, "provider": "io"} for a in agents if isinstance(a, dict) and "id" in a]

    def get_models(self, task: str = None, provider: str = None) -> List[Dict[str, Any]]:
        # Filter by task/provider if specified
        results = self.models
        if task:
            results = [m for m in results if task in m.get('tasks', [])]
        if provider:
            results = [m for m in results if m.get('provider') == provider]
        return results

    def get_agents(self, provider: str = None) -> List[Dict[str, Any]]:
        results = self.agents
        if provider:
            results = [a for a in results if a.get('provider') == provider]
        return results

# Usage example (to be used in main.py or routers):
# registry = ModelRegistry()
# registry.discover_all()
# models = registry.get_models(task="text-generation")
