from flask import Blueprint, jsonify, g
from auth.decorators import jwt_required, require_role

rbac_test_bp = Blueprint("rbac_test", __name__)


@rbac_test_bp.route("/test/reporter-action", methods=["POST"])
@jwt_required
@require_role(["REPORTER", "EDITOR"])
def reporter_action():
    return jsonify({
        "status": "success",
        "message": f"Reporter action executed successfully by {g.user['name']} ({g.user['role']}).",
        "actor": g.user
    }), 200


@rbac_test_bp.route("/test/publish", methods=["POST"])
@jwt_required
@require_role(["EDITOR"])
def publish_story():
    """Only EDITOR can publish. REPORTER attempting this endpoint receives 403 Forbidden."""
    return jsonify({
        "status": "success",
        "message": f"Publication approved and executed by Editor {g.user['name']}.",
        "actor": g.user
    }), 200


@rbac_test_bp.route("/test/deskhead-analytics", methods=["GET"])
@jwt_required
@require_role(["DESK_HEAD", "EDITOR"])
def deskhead_analytics():
    return jsonify({
        "status": "success",
        "message": f"Desk Head analytics accessed by {g.user['name']} ({g.user['role']}).",
        "actor": g.user
    }), 200
