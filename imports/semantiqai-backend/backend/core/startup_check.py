import os
from backend.core.config import APP_NAME, APP_ENV, APP_PORT

def validate_startup():
    issues = []

    if not APP_NAME:
        issues.append("APP_NAME missing")

    if not APP_PORT:
        issues.append("APP_PORT missing")

    return issues
