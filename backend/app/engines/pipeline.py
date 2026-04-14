import os
from .planner import build_video_plan
from .thumbnail import generate_thumbnail
from .slides import render_scene_card
from .subtitles import generate_srt
from .tts import synthesize_voice
from .assembler import assemble_video
from .utils import project_paths, ensure_project_dir, save_json

def build_founder_video(topic: str, style: str = "viral faceless youtube"):
    paths = project_paths(topic)
    ensure_project_dir(paths)

    plan = build_video_plan(topic, style=style)
    title = plan.get("title") or topic
    scenes = plan.get("scenes") or []

    thumbnail_path = generate_thumbnail(
        plan.get("thumbnail_text", "WATCH THIS"),
        paths["thumbnail_path"],
        title=title
    )

    image_paths = []
    durations = []
    full_voiceover_parts = []

    for i, scene in enumerate(scenes, start=1):
        image_path = os.path.join(paths["project_dir"], f"scene_{i:02}.png")
        render_scene_card(scene, image_path, title=title)
        image_paths.append(image_path)
        durations.append(scene.get("duration_sec", 6))
        full_voiceover_parts.append(scene.get("voiceover", ""))

    full_voiceover = "\\n\\n".join([p for p in full_voiceover_parts if p]).strip()
    if not full_voiceover:
        full_voiceover = f"This is an auto generated founder video about {topic}."

    synthesize_voice(full_voiceover, paths["audio_path"])
    generate_srt(scenes, paths["subs_path"])

    assemble_video(
        image_paths=image_paths,
        durations=durations,
        audio_path=paths["audio_path"],
        subs_path=paths["subs_path"],
        output_path=paths["video_path"],
        concat_path=paths["concat_path"]
    )

    manifest = {
        "topic": topic,
        "style": style,
        "title": title,
        "description": plan.get("description", ""),
        "tags": plan.get("tags", []),
        "thumbnail_text": plan.get("thumbnail_text", ""),
        "thumbnail_path": thumbnail_path,
        "video_path": paths["video_path"],
        "audio_path": paths["audio_path"],
        "subs_path": paths["subs_path"],
        "project_id": paths["id"],
        "scene_count": len(scenes)
    }
    save_json(paths["manifest_path"], manifest)
    return manifest

