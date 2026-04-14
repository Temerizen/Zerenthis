from flask import Flask, jsonify
from backend.core.config import APP_HOST, APP_PORT, DEBUG, APP_NAME
from backend.core.db import init_db
from backend.core.logging_setup import setup_logging
from backend.core.startup_check import validate_startup

from backend.routes.health import health_bp
from backend.routes.ai import ai_bp
from backend.routes.factory import factory_bp
from backend.routes.lab import lab_bp
from backend.routes.founder import founder_bp

def create_app():
    setup_logging()
    init_db()

    issues = validate_startup()
    if issues:
        print("Startup warnings:", issues)

    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    app.register_blueprint(health_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(factory_bp)
    app.register_blueprint(lab_bp)
    app.register_blueprint(founder_bp)

    @app.get("/")
    def index():
        return jsonify({
            "ok": True,
            "app": APP_NAME,
            "status": "stable",
            "message": "SemantiqAI fully stabilized core online"
        })

    from backend.core.error_handler import register_error_handlers
    register_error_handlers(app)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host=APP_HOST, port=APP_PORT, debug=DEBUG)

