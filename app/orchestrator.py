import time
import logging

class Orchestrator:
    def __init__(self, model_selector, tool_registry):
        self.model_selector = model_selector
        self.tool_registry = tool_registry

    def orchestrate(self, task, steps):
        results = []
        for step in steps:
            tool = self.tool_registry.tools.get(step['tool'])
            if not tool:
                results.append({"error": f"Tool {step['tool']} not found"})
                continue
            retries = 0
            while retries < 3:
                try:
                    result = tool(*step.get('args', []), **step.get('kwargs', {}))
                    if self.validate(result):
                        results.append(result)
                        break
                    else:
                        retries += 1
                except Exception as e:
                    logging.error(f"Orchestration error: {e}")
                    retries += 1
            else:
                results.append({"error": f"Step {step['tool']} failed after retries"})
        return results

    def validate(self, result):
        # Placeholder: always true, can add more logic
        return True
