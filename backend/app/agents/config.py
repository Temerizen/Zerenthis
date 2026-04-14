import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

APP_NAME = os.getenv("APP_NAME", "SemantiqAI")
APP_ENV = os.getenv("APP_ENV", "development")
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "5000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

JWT_SECRET = os.getenv("JWT_SECRET", "change_this_to_a_long_random_secret")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4")

FOUNDER_KEY = os.getenv("FOUNDER_KEY", "")
FOUNDER_NAME = os.getenv("FOUNDER_NAME", "Founder")
FOUNDER_MODE = os.getenv("FOUNDER_MODE", "enabled").lower() == "enabled"

DATA_DIR = ROOT_DIR / "backend" / "data"
LOG_DIR = ROOT_DIR / "backend" / "logs"
MEMORY_DIR = ROOT_DIR / "backend" / "memory"
EXPORT_DIR = ROOT_DIR / "exports"
YOUTUBE_DIR = EXPORT_DIR / "youtube"
SOCIAL_DIR = EXPORT_DIR / "social"
PDF_DIR = EXPORT_DIR / "pdf"
EMAIL_DIR = EXPORT_DIR / "email"
THUMBNAIL_DIR = EXPORT_DIR / "thumbnails"
BATCH_DIR = EXPORT_DIR / "batches"
INDEX_DIR = EXPORT_DIR / "index"
EDUCATION_DIR = EXPORT_DIR / "education"
EDUCATION_PLAN_DIR = EDUCATION_DIR / "plans"
EDUCATION_LESSON_DIR = EDUCATION_DIR / "lessons"
EDUCATION_ASSESSMENT_DIR = EDUCATION_DIR / "assessments"
COGNITIVE_DIR = EXPORT_DIR / "cognitive"
COGNITIVE_DRILL_DIR = COGNITIVE_DIR / "drills"
COGNITIVE_REPORT_DIR = COGNITIVE_DIR / "reports"
SIMULATION_DIR = EXPORT_DIR / "simulation"
SIMULATION_SCENARIO_DIR = SIMULATION_DIR / "scenarios"
GROWTH_DIR = EXPORT_DIR / "growth"
GROWTH_PLAN_DIR = GROWTH_DIR / "plans"
FOUNDER_EXPORT_DIR = EXPORT_DIR / "founder"
FOUNDER_REPORT_DIR = FOUNDER_EXPORT_DIR / "reports"

for folder in [
    DATA_DIR, LOG_DIR, MEMORY_DIR, EXPORT_DIR, YOUTUBE_DIR, SOCIAL_DIR, PDF_DIR,
    EMAIL_DIR, THUMBNAIL_DIR, BATCH_DIR, INDEX_DIR, EDUCATION_DIR,
    EDUCATION_PLAN_DIR, EDUCATION_LESSON_DIR, EDUCATION_ASSESSMENT_DIR,
    COGNITIVE_DIR, COGNITIVE_DRILL_DIR, COGNITIVE_REPORT_DIR,
    SIMULATION_DIR, SIMULATION_SCENARIO_DIR, GROWTH_DIR, GROWTH_PLAN_DIR,
    FOUNDER_EXPORT_DIR, FOUNDER_REPORT_DIR
]:
    folder.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "semantiqai.db"

