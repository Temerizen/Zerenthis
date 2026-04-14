from backend.ai_engine import generate_text

def generate_video_script(topic):
    prompt = f"""
Create a HIGHLY engaging YouTube video script.

Topic: {topic}

Requirements:
- Hook in first 3 seconds
- Viral pacing
- Emotional + curiosity driven
- Clean structure
- Title included
- Sections clearly separated
- Maximize retention

Also include:
- thumbnail text ideas
- video description
- tags
"""
    return generate_text(prompt)

