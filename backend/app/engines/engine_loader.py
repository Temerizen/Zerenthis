import os
import importlib
from typing import Dict, Any

ENGINE_REGISTRY = {}

def load_engines():
    base = os.path.dirname(__file__)
    for file in os.listdir(base):
        if file.endswith(".py") and file not in ["engine_loader.py"]:
            module_name = f"backend.app.engines.{file[:-3]}"
            try:
                mod = importlib.import_module(module_name)
                if hasattr(mod, "run"):
                    ENGINE_REGISTRY[file[:-3]] = mod.run
            except Exception as e:
                print(f"[ENGINE LOAD ERROR] {module_name}: {e}")

def run_engine(name: str, payload: Dict[str, Any]):
    if name not in ENGINE_REGISTRY:
        return {"error": f"Engine '{name}' not found"}
    try:
        return ENGINE_REGISTRY[name](payload)
    except Exception as e:
        return {"error": str(e)}

load_engines()
