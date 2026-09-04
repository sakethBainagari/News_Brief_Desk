from flask import Blueprint, jsonify, g
from auth.decorators import jwt_required, require_role
from db.workflow_queries import reset_demo_data_in_db

demo_bp = Blueprint("demo", __name__)


@demo_bp.route("/demo/reset", methods=["POST"])
@jwt_required
@require_role("DESK_HEAD")
def reset_demo():
    """
    CRITICAL WORKFLOW REQUIREMENT: Allowed ONLY for DESK_HEAD role.
    Reporter or Editor calling this receives 403 Forbidden.
    Resets generated workflow stories, briefs, merges, and audit activity while preserving raw_items (81) and users (3).
    """
    try:
        actor_id = getattr(g, "user_id", None)
        result = reset_demo_data_in_db(actor_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "error": "Reset Error",
            "message": f"Failed to reset demo data: {str(e)}"
        }), 500
