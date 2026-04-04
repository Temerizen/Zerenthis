import subprocess
from backend.app.core.codegen import generate_code

def fix_file(path):
    try:
        subprocess.check_output(["python", "-m", "py_compile", path])
        return {"status": "ok"}
    except Exception as e:
        prompt = f"""
Fix this Python file error:

{path}

Error:
{str(e)}

Return FULL corrected file.
"""
        code = generate_code(prompt)
        open(path, "w", encoding="utf-8").write(code)
        return {"status": "fixed", "file": path}