"""
Compatibility shim to run the advanced backend API.
"""

import importlib.util
import sys
from pathlib import Path

BACKEND_API_PATH = Path(__file__).parent / "backend" / "api.py"

spec = importlib.util.spec_from_file_location("backend_api", BACKEND_API_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("Failed to load backend API module")

backend_api = importlib.util.module_from_spec(spec)
sys.modules["backend_api"] = backend_api
spec.loader.exec_module(backend_api)

app = backend_api.app

if __name__ == "__main__":
    backend_api.app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
