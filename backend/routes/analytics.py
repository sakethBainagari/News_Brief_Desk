from flask import Blueprint, jsonify
from auth.decorators import jwt_required, require_role
from db.analytics_queries import get_desk_head_analytics, get_audit_logs

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics", methods=["GET"])
@jwt_required
@require_role("DESK_HEAD")
def get_analytics():
    """
    CRITICAL WORKFLOW REQUIREMENT: Allowed ONLY for DESK_HEAD role.
    Reporter or Editor attempting this endpoint receives 403 Forbidden.
    """
    try:
        data = get_desk_head_analytics()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": "Database Query Error", "message": "Unable to calculate analytics metrics."}), 500


@analytics_bp.route("/audit-logs", methods=["GET"])
@jwt_required
@require_role("DESK_HEAD")
def list_audit_logs():
    try:
        logs = get_audit_logs(limit=50)
        return jsonify({"logs": logs}), 200
    except Exception as e:
        return jsonify({"error": "Database Query Error", "message": "Unable to retrieve audit logs."}), 500
