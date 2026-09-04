import uuid
from flask import Blueprint, request, jsonify, g
from auth.decorators import jwt_required, require_role
from db.workflow_queries import merge_story_clusters

merge_bp = Blueprint("merge", __name__)


@merge_bp.route("/stories/merge", methods=["POST"])
@jwt_required
@require_role(["EDITOR"])
def merge_stories_route():
    """
    CRITICAL WORKFLOW REQUIREMENT: Allowed ONLY for EDITOR role.
    Merges source_story_id into target_story_id, preserving source articles and audit history.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad Request", "message": "Missing JSON payload."}), 400

    source_story_id = data.get("source_story_id")
    target_story_id = data.get("target_story_id")
    reason = data.get("reason", "Editor initiated story cluster merge.")

    if not source_story_id or not target_story_id:
        return jsonify({
            "error": "Bad Request",
            "message": "Both 'source_story_id' and 'target_story_id' are required parameters."
        }), 400

    try:
        uuid.UUID(source_story_id)
        uuid.UUID(target_story_id)
    except ValueError:
        return jsonify({"error": "Invalid Format", "message": "Story IDs must be valid UUIDs."}), 400

    try:
        result = merge_story_clusters(source_story_id, target_story_id, g.user["sub"], reason)
        return jsonify({
            "status": "success",
            "message": f"Story cluster '{source_story_id}' merged into '{target_story_id}' successfully.",
            "data": result
        }), 200
    except ValueError as ve:
        return jsonify({"error": "Workflow Error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "Database Error", "message": f"Failed to merge story clusters: {str(e)}"}), 500
