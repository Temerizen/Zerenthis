import os
from .utils import find_ffmpeg, run

def make_scene_clips(image_paths, durations, concat_path):
    with open(concat_path, "w", encoding="utf-8") as f:
        for img, dur in zip(image_paths, durations):
            img_norm = img.replace("\\", "/")
            f.write("file '{img_norm}'\\n")
            f.write("duration {float(dur):.2f}\\n")
        if image_paths:
            last = image_paths[-1].replace("\\", "/")
            f.write("file '{last}'\\n")
    return concat_path

def assemble_video(image_paths, durations, audio_path, subs_path, output_path, concat_path):
    ffmpeg = find_ffmpeg()
    make_scene_clips(image_paths, durations, concat_path)

    vf = (
        "subtitles={subs_path.replace(chr(92), '/').replace(':', '\\:')}:"
        "force_style='FontSize=18,PrimaryColour=&H00FFFFFF&,OutlineColour=&H00000000&,BorderStyle=3,Outline=1'"
    )

    cmd = [
        ffmpeg,
        "-y",
        "-", "concat",
        "-safe", "0",
        "-i", concat_path,
        "-i", audio_path,
        "-vf", vf,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]
    run(cmd)
    return output_path

