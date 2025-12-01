# app/utils/generate_registry.py
"""
Dev utility: generate a file describing local API registry discovered by local_api_dispatcher.
Usage:
    python -m app.utils.generate_registry     # or run with your Python interpreter
This will attempt to import the routes.api package and write registry to ./.local_api_registry.json
"""

import os
from pathlib import Path
from utils.local_api_dispatcher import export_registry

OUT_JSON = Path(os.getcwd()) / ".local_api_registry.json"
OUT_PY = Path(os.getcwd()) / "local_api_registry.py"

if __name__ == "__main__":
    print("Generating local API registry...")
    try:
        export_registry(str(OUT_JSON), fmt="json")
        export_registry(str(OUT_PY), fmt="py")
        print(f"Wrote registry to {OUT_JSON} and {OUT_PY}")
    except Exception as e:
        print("Failed to export registry:", e)
