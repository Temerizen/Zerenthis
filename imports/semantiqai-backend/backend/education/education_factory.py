from pathlib import Path
from backend.core.config import EDUCATION_PLAN_DIR, EDUCATION_LESSON_DIR, EDUCATION_ASSESSMENT_DIR
from backend.utils.files import slugify, timestamp
from backend.utils.writer import write_text_file
from backend.education.paths.planner import build_learning_path
from backend.education.content.lesson_builder import build_lesson, render_lesson_markdown
from backend.education.assessments.assessment_builder import build_assessment, render_assessment_markdown
from backend.education.run_log import log_education_run

def generate_learning_plan(subject: str, level: str) -> dict:
    title = f"{subject} | {level} learning plan"
    path_steps = build_learning_path(subject, level)
    content = "# " + title + "\n\n## Path\n" + "\n".join([f"- {x}" for x in path_steps]) + "\n"
    filename = f"{timestamp()}_{slugify(subject)}_{slugify(level)}_learning_plan.md"
    output_path = write_text_file(Path(EDUCATION_PLAN_DIR) / filename, content)
    log_education_run("learning_plan", subject, level, title, output_path)
    return {"run_type": "learning_plan", "title": title, "output_path": output_path}

def generate_lesson(subject: str, level: str, topic: str) -> dict:
    data = build_lesson(subject, level, topic)
    filename = f"{timestamp()}_{slugify(subject)}_{slugify(topic)}_{slugify(level)}_lesson.md"
    output_path = write_text_file(Path(EDUCATION_LESSON_DIR) / filename, render_lesson_markdown(data))
    log_education_run("lesson", subject, level, data["title"], output_path)
    return {"run_type": "lesson", "title": data["title"], "output_path": output_path}

def generate_assessment(subject: str, level: str, topic: str) -> dict:
    data = build_assessment(subject, level, topic)
    filename = f"{timestamp()}_{slugify(subject)}_{slugify(topic)}_{slugify(level)}_assessment.md"
    output_path = write_text_file(Path(EDUCATION_ASSESSMENT_DIR) / filename, render_assessment_markdown(data))
    log_education_run("assessment", subject, level, data["title"], output_path)
    return {"run_type": "assessment", "title": data["title"], "output_path": output_path}

def generate_subject_pack(subject: str, level: str, topic: str) -> dict:
    return {
        "subject": subject,
        "level": level,
        "topic": topic,
        "plan": generate_learning_plan(subject, level),
        "lesson": generate_lesson(subject, level, topic),
        "assessment": generate_assessment(subject, level, topic)
    }
