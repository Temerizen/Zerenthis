from backend.founder_video.pipeline import build_founder_video
from .exporter import export_all_formats
from .captions import generate_captions

def full_distribution_pipeline(topic):
    video_data = build_founder_video(topic)

    exports = export_all_formats(video_data["video_path"])
    captions = generate_captions(topic)

    return {
        "video": video_data,
        "exports": exports,
        "captions": captions
    }

