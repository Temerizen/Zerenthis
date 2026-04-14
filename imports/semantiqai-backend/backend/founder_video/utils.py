import os
import re
import json
import shutil
import subprocess
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_ROOT = os.path.join(ROOT, "outputs", "empire_content")
VIDEO_DIR = os.path.join(OUTPUT_ROOT, "videos")
AUDIO_DIR = os.path.join(OUTPUT_ROOT, "audio")
IMAGE_DIR = os.path.join(OUTPUT_ROOT, "images")
SUB_DIR = os.path.join(OUTPUT_ROOT, "subs")
PROJECT_DIR = os.path.join(OUTPUT_ROOT, "projects")

for path in [VIDEO_DIR, AUDIO_DIR, IMAGE_DIR, SUB_DIR, PROJECT_DIR]:
    os.makedirs(path, exist_ok=True)

def slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "project"

def timestamp_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def project_paths(topic: str):
    slug = slugify(topic)
    stamp = timestamp_id()
    base = f"{slug}_{stamp}"
    return {
        "id": base,
        "project_dir": os.path.join(PROJECT_DIR, base),
        "video_path": os.path.join(VIDEO_DIR, f"{base}.mp4"),
        "audio_path": os.path.join(AUDIO_DIR, f"{base}.wav"),
        "subs_path": os.path.join(SUB_DIR, f"{base}.srt"),
        "thumbnail_path": os.path.join(IMAGE_DIR, f"{base}_thumbnail.png"),
        "manifest_path": os.path.join(PROJECT_DIR, base, "manifest.json"),
        "concat_path": os.path.join(PROJECT_DIR, base, "concat.txt"),
    }

def ensure_project_dir(paths: dict):
    os.makedirs(paths["project_dir"], exist_ok=True)

def find_ffmpeg() -> str:
    local_ffmpeg = os.path.join(ROOT, "backend", "bin", "ffmpeg.exe")
    if os.path.exists(local_ffmpeg):
        return local_ffmpeg
    in_path = shutil.which("ffmpeg")
    if in_path:
        return in_path
    raise FileNotFoundError(
        "FFmpeg not found. Put ffmpeg.exe in backend/bin or add FFmpeg to PATH."
    )

def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            "Command failed\\n"
            f"CMD: {' '.join(cmd)}\\n"
            f"STDOUT:\\n{result.stdout}\\n"
            f"STDERR:\\n{result.stderr}"
        )
    return result

def save_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
