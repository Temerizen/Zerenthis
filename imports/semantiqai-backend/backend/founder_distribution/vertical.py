import os
import subprocess
from backend.founder_video.utils import find_ffmpeg

def create_vertical_version(input_video, output_video):
    ffmpeg = find_ffmpeg()

    cmd = [
        ffmpeg,
        "-y",
        "-i", input_video,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:a", "copy",
        output_video
    ]

    subprocess.run(cmd, check=True)
    return output_video
