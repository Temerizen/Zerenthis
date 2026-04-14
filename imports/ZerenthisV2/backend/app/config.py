import os

APP_NAME = os.getenv("APP_NAME", "Zerenthis V2")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
