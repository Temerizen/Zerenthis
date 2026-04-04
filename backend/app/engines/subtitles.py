def format_srt_time(seconds: float) -> str:
    total_ms = int(seconds * 1000)
    hrs = total_ms // 3600000
    mins = (total_ms % 3600000) // 60000
    secs = (total_ms % 60000) // 1000
    ms = total_ms % 1000
    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"

def generate_srt(scenes, output_path: str):
    lines = []
    current = 0.0

    for idx, scene in enumerate(scenes, start=1):
        dur = float(scene.get("duration_sec", 6))
        text = (scene.get("voiceover") or scene.get("onscreen_text") or f"Scene {idx}").strip()
        start = format_srt_time(current)
        end = format_srt_time(current + dur)
        lines.append(str(idx))
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")
        current += dur

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\\n".join(lines))

    return output_path
