from .storage import append_log
from .health import health_summary

def founder_overview():
    health = health_summary()
    return {
        "title": "SemantiqAI Founder Control Layer",
        "empire_status": "founder_control_active",
        "health": health,
        "priority_queue": [
            "Auth / roles / security hardening",
            "Frontend transformation",
            "Deployment prep",
            "Final stabilization sweep",
            "UI sweep"
        ]
    }

def register_manual_action(action_name: str, metadata=None):
    return append_log(action_name, metadata or {})

