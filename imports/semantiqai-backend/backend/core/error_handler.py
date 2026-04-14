from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify({
            "ok": False,
            "error": "internal_error",
            "message": str(e)
        }), 500
