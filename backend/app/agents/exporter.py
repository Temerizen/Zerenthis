import os
from .vertical import create_vertical_version

def export_all_formats(video_path):
    base = os.path.splitext(video_path)[0]

    vertical = base + "_vertical.mp4"
    square = base + "_square.mp4"

    results = {}

    # Vertical (TikTok / Shorts)
    try:
        create_vertical_version(video_path, vertical)
        results["vertical"] = vertical
    except Exception as e:
        results["vertical_error"] = str(e)

    # Square version (Instagram feed)
    try:
        import subprocess
        from backend.founder_video.utils import find_ffmpeg

        ffmpeg = find_ffmpeg()
        cmd = [
            ffmpeg,
            "-y",
            "-i", video_path,
            "-vf", "scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080",
            "-c:a", "copy",
            square
        ]
        subprocess.run(cmd, check=True)
        results["square"] = square
    except Exception as e:
        results["square_error"] = str(e)

    results["original"] = video_path
    return results

