import importlib


def run_tests():
    checks = []

    try:
        importlib.import_module("backend.app.main")
        checks.append(("import backend.app.main", True))
    except Exception:
        checks.append(("import backend.app.main", False))

    try:
        importlib.import_module("backend.Engine.product_engine")
        checks.append(("import backend.Engine.product_engine", True))
    except Exception:
        checks.append(("import backend.Engine.product_engine", False))

    try:
        importlib.import_module("backend.Engine.video_engine")
        checks.append(("import backend.Engine.video_engine", True))
    except Exception:
        checks.append(("import backend.Engine.video_engine", False))

    return all(ok for _, ok in checks), checks
