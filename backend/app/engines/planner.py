import json
import re
from backend.ai_engine import generate_text

def _extract_json_block(text: str):
    if not text:
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"`json\s*(.*?)\s*`", text, re.DOTALL | re.IGNORECASE)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    return None

def build_video_plan(topic: str, style: str = "viral faceless youtube"):
    prompt = f'''
Create a JSON video production plan for this topic: "{topic}"

Style: {style}

Return ONLY valid JSON with this exact structure:
{{
  "title": "string",
  "hook": "string",
  "description": "string",
  "thumbnail_text": "1 to 5 words",
  "tags": ["tag1", "tag2", "tag3"],
  "scenes": [
    {{
      "scene_number": 1,
      "headline": "string",
      "voiceover": "2 to 5 sentences",
      "visual_prompt": "describe the visual for a cinematic background card",
      "onscreen_text": "short punchy phrase",
      "duration_sec": 6
    }}
  ]
}}

Requirements:
- 6 to 10 scenes
- strong opening hook
- retention-focused pacing
- durations between 5 and 9 seconds
- no markdown
- no commentary
'''
    raw = generate_text(prompt, temperature=0.8, max_tokens=1800)
    parsed = _extract_json_block(raw)

    if isinstance(parsed, dict) and parsed.get("scenes"):
        return parsed

    return {
        "title": topic,
        "hook": f"You are about to discover the hidden truth about {topic}.",
        "description": f"Auto-generated founder video package for {topic}.",
        "thumbnail_text": "WATCH THIS",
        "tags": ["ai", "automation", "founder"],
        "scenes": [
            {
                "scene_number": 1,
                "headline": "Hook",
                "voiceover": f"Here is why {topic} matters more than most people realize.",
                "visual_prompt": f"Bold cinematic background for {topic}",
                "onscreen_text": "START HERE",
                "duration_sec": 6
            },
            {
                "scene_number": 2,
                "headline": "Core Idea",
                "voiceover": f"The core idea behind {topic} is leverage, clarity, and execution.",
                "visual_prompt": f"High contrast motion graphic concept for {topic}",
                "onscreen_text": "THE CORE",
                "duration_sec": 6
            },
            {
                "scene_number": 3,
                "headline": "Why It Wins",
                "voiceover": f"When used properly, {topic} compounds faster than scattered effort.",
                "visual_prompt": f"Momentum and growth visual for {topic}",
                "onscreen_text": "WHY IT WINS",
                "duration_sec": 6
            }
        ]
    }
