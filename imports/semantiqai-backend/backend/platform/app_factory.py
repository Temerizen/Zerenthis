import importlib
from flask import Flask, request
from backend.platform.config import Settings, as_dict
from backend.platform.logger import log_event
from backend.platform.responses import ok, fail
from backend.platform.registry import MODULE_REGISTRY
from backend.platform.security_headers import apply_security_headers
from backend.platform.rate_limit import is_limited

def _apply_basic_cors(response):
    response.headers["Access-Control-Allow-Origin"] = Settings.FRONTEND_ORIGIN
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, x-founder-key"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    return response

def _register_blueprints(app):
    registered = []
    failed = []

    for mod in MODULE_REGISTRY:
        try:
            module = importlib.import_module(mod["import_path"])
            blueprint = getattr(module, mod["blueprint_name"])
            app.register_blueprint(blueprint)
            registered.append({
                "name": mod["name"],
                "blueprint": mod["blueprint_name"],
                "group": mod["group"]
            })
        except Exception as e:
            failed.append({
                "name": mod["name"],
                "error": str(e)
            })

    app.config["REGISTERED_MODULES"] = registered
    app.config["FAILED_MODULES"] = failed
    return registered, failed

def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = Settings.MAX_REQUEST_SIZE
    app.config["SECRET_KEY"] = Settings.SECRET_KEY

    @app.before_request
    def _rate_limit():
        if request.method == "OPTIONS":
            return ok({"preflight": True}, "preflight")
        ip = request.remote_addr or "unknown"
        if is_limited(ip):
            return fail("rate limit exceeded", 429, "rate_limit")

    @app.before_request
    def _before_request():
        if request.method != "OPTIONS":
            log_event("request", {
                "method": request.method,
                "path": request.path
            })

    @app.after_request
    def _secure(response):
        response = apply_security_headers(response)
        return response

    @app.after_request
    def _after_request(response):
        if Settings.ENABLE_CORS:
            response = _apply_basic_cors(response)
        return response

    @app.errorhandler(404)
    def _not_found(_):
        return fail("route not found", 404, "not_found")

    @app.errorhandler(405)
    def _method_not_allowed(_):
        return fail("method not allowed", 405, "method_not_allowed")

    @app.errorhandler(500)
    def _internal(_):
        return fail("internal server error", 500, "internal_error")

    @app.route("/", methods=["GET"])
    def root():
        return ok({
            "name": Settings.APP_NAME,
            "version": Settings.VERSION,
            "env": Settings.APP_ENV
        }, "SemantiqAI backend online")

    @app.route("/status", methods=["GET"])
    def status():
        return ok({
            "config": as_dict(),
            "registered_modules": app.config.get("REGISTERED_MODULES", []),
            "failed_modules": app.config.get("FAILED_MODULES", [])
        }, "status")

    @app.route("/integration/report", methods=["GET"])
    def integration_report():
        try:
            from backend.integration.doctor import run_doctor
            return ok(run_doctor(), "integration_report")
        except Exception as e:
            return fail("integration report unavailable", 500, "integration_report_failed", {"message": str(e)})

    _register_blueprints(app)
    return app
