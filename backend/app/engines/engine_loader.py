import importlib

ENGINE_MODULES = [
    "backend.app.engines.builder_engine",
    "backend.app.engines.executor_worker",
    "backend.app.engines.local_test",
    "backend.app.engines.autopilot_loop"
]

def load_engines():
    loaded = []

    for module_name in ENGINE_MODULES:
        try:
            module = importlib.import_module(module_name)

            if hasattr(module, "run"):
                loaded.append(module)
            else:
                print(f"[ENGINE SKIP] {module_name}: no run()")

        except Exception as e:
            print(f"[ENGINE ERROR] {module_name}: {e}")

    return loaded
