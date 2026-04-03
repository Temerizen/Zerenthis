from pathlib import Path
import importlib.util

target = Path(__file__).resolve().parents[1] / "backend" / "app" / "main.py"
spec = importlib.util.spec_from_file_location("zerenthis_backend_main", target)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
app = module.app