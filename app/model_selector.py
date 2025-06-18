import yaml
from .task_classifier import TaskClassifier

class ModelSelector:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.models = self.config.get("models", [])

    def select(self, task: str, tags=None):
        tags = tags or []
        # Prefer models that match the task and tags
        for m in self.models:
            if task in m.get("tasks", []):
                if not tags or any(tag in m.get("tags", []) for tag in tags):
                    return m["id"]
        # Fallback: return first model for the task
        for m in self.models:
            if task in m.get("tasks", []):
                return m["id"]
        # Fallback: return first model
        return self.models[0]["id"] if self.models else None
