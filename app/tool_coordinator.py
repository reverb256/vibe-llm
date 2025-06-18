import subprocess
from typing import Dict

class ToolCoordinator:
    def run_shell(self, command: str) -> Dict:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
        except Exception as e:
            return {"error": str(e)}

    def read_file(self, path: str) -> Dict:
        try:
            with open(path, "r") as f:
                return {"content": f.read()}
        except Exception as e:
            return {"error": str(e)}

    def write_file(self, path: str, content: str) -> Dict:
        try:
            with open(path, "w") as f:
                f.write(content)
            return {"status": "written"}
        except Exception as e:
            return {"error": str(e)}
