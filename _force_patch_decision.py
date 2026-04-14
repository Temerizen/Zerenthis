from pathlib import Path
import py_compile

p = Path("backend/app/engines/decision_engine.py")
lines = p.read_text(encoding="utf-8").splitlines()

new_lines = []
patched = False

for line in lines:
    if '"score":' in line and 'round(' in line and 'final' in line and 'apply_self_influence' not in line:
        indent = line[:len(line) - len(line.lstrip())]
        new_line = f'{indent}"score": round(apply_self_influence(name, final), 2),'
        new_lines.append(new_line)
        patched = True
    else:
        new_lines.append(line)

if patched:
    p.write_text("\n".join(new_lines), encoding="utf-8")
    py_compile.compile(str(p), doraise=True)
    print("FREE WILL SUCCESSFULLY INJECTED")
else:
    print("NO MATCH FOUND — CHECK MANUALLY")

