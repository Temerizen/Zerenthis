import random

def build_trailer_script(girlfriend_mode=False):
    if girlfriend_mode:
        return [
            "I didn’t just want to say something to you...",
            "I wanted to create something you could feel.",
            "So I built a little world… just for you.",
            "A place where everything is soft, warm… and real.",
            "Where every moment quietly says… you matter.",
            "Because you are the reason it all feels alive.",
            "This isn’t just a video.",
            "It’s something I made… for you. Always."
        ]
    else:
        return [
            "One idea changed everything.",
            "It started small… almost nothing.",
            "Then it became something more.",
            "A world. A system. A story.",
            "Built from imagination.",
            "Driven by creation.",
            "This is where it begins.",
            "This… is Zerenthis."
        ]

def build_trailer_timing(lines):
    timings = []
    base = 2.2
    
    for i, line in enumerate(lines):
        if i < 2:
            timings.append(base)
        elif i < 5:
            timings.append(base + 0.5)
        else:
            timings.append(base + 1.0)
    
    return timings

def trailer_prompt_boost(line, girlfriend_mode=False):
    if girlfriend_mode:
        return f"romantic cinematic scene, emotional, soft warm lighting, couple energy, ultra realistic, volumetric lighting, 8k, {line}"
    else:
        return f"cinematic dramatic scene, high intensity, ultra detailed, 8k, {line}"

