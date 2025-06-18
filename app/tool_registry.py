import os
import importlib
from typing import Dict, Callable

class ToolRegistry:
    def __init__(self, tools_dir="app/tools"):
        self.tools_dir = tools_dir
        self.tools = self._discover_tools()

    def _discover_tools(self) -> Dict[str, Callable]:
        tools = {}
        if not os.path.exists(self.tools_dir):
            return tools
        for fname in os.listdir(self.tools_dir):
            if fname.endswith(".py") and not fname.startswith("_"):
                modname = fname[:-3]
                mod = importlib.import_module(f"app.tools.{modname}")
                if hasattr(mod, "run"):
                    tools[modname] = mod.run
        return tools

    def list_tools(self):
        return list(self.tools.keys())

    def run_tool(self, name, *args, **kwargs):
        if name in self.tools:
            return self.tools[name](*args, **kwargs)
        return {"error": f"Tool {name} not found"}
