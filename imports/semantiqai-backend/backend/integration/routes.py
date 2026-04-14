from flask import Blueprint, jsonify
from backend.platform.module_map import get_module_map

integration = Blueprint("integration", __name__)

@integration.route("/integration/modules", methods=["GET"])
def modules():
    return jsonify({
        "ok": True,
        "data": get_module_map()
    })
