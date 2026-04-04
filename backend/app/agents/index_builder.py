from pathlib import Path
from backend.core.config import INDEX_DIR
from backend.utils.writer import write_text_file

def rebuild_master_index(entries: list[dict]) -> str:
    cards = []

    for item in entries:
        cards.append(f"""
        <div class="card">
            <div class="type">{item.get("content_type", "unknown").upper()}</div>
            <h3>{item.get("title", "Untitled")}</h3>
            <p><strong>Topic:</strong> {item.get("topic", "")}</p>
            <p><strong>Created:</strong> {item.get("created_at", "")}</p>
            <p><strong>Path:</strong> {item.get("output_path", "")}</p>
        </div>
        """)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>SemantiqAI Content Index</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{ font-family: Arial, sans-serif; background: #0b1020; color: #f5f7fb; margin: 0; padding: 32px; }}
    h1 {{ margin-top: 0; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
    .card {{ background: #141b34; border: 1px solid #2b355e; border-radius: 16px; padding: 18px; }}
    .type {{ font-size: 12px; opacity: .75; margin-bottom: 8px; }}
    p {{ line-height: 1.4; word-break: break-word; }}
  </style>
</head>
<body>
  <h1>SemantiqAI Content Factory</h1>
  <p>Generated outputs index.</p>
  <div class="grid">
    {''.join(cards) if cards else '<p>No content generated yet.</p>'}
  </div>
</body>
</html>
"""
    return write_text_file(Path(INDEX_DIR) / "master_index.html", html)
