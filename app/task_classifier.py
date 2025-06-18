import re
from typing import Dict

# Simple rule-based classifier for MVP
class TaskClassifier:
    def classify(self, prompt: str) -> str:
        prompt = prompt.lower()
        if any(word in prompt for word in ["fix", "bug", "error", "debug"]):
            return "debugging"
        if any(word in prompt for word in ["refactor", "clean up", "improve"]):
            return "refactoring"
        if any(word in prompt for word in ["doc", "documentation", "explain"]):
            return "documentation"
        if any(word in prompt for word in ["search", "google", "web"]):
            return "internet-search"
        if any(word in prompt for word in ["file", "read", "write", "open"]):
            return "file-operations"
        return "code-generation"
