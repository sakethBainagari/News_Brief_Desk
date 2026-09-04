import uuid
from flask import Blueprint, request, jsonify, g
from auth.decorators import jwt_required, require_role
from db.workflow_queries import edit_brief, submit_brief, publish_brief, get_brief_by_id

briefs_bp = Blueprint("briefs", __name__)


@briefs_bp.route("/briefs/<brief_id>", methods=["GET"])
@jwt_required
def get_brief(brief_id: str):
    try:
        uuid.UUID(brief_id)
    except ValueError:
        return jsonify({"error": "Invalid Format", "message": f"'{brief_id}' is not a valid UUID."}), 400

    brief = get_brief_by_id(brief_id)
    if not brief:
        return jsonify({"error": "Not Found", "message": f"Brief '{brief_id}' was not found."}), 404

    return jsonify(brief), 200


@briefs_bp.route("/briefs/<brief_id>", methods=["PUT"])
@jwt_required
@require_role(["REPORTER", "EDITOR"])
def update_brief(brief_id: str):
    try:
        uuid.UUID(brief_id)
    except ValueError:
        return jsonify({"error": "Invalid Format", "message": f"'{brief_id}' is not a valid UUID."}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad Request", "message": "Missing JSON payload."}), 400

    headline = data.get("headline")
    summary = data.get("summary")

    if not headline or not summary:
        return jsonify({"error": "Bad Request", "message": "Both 'headline' and 'summary' are required."}), 400

    try:
        updated = edit_brief(brief_id, headline, summary, g.user["sub"])
        return jsonify({"status": "success", "brief": updated}), 200
    except ValueError as ve:
        return jsonify({"error": "Workflow Error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "Database Error", "message": "Failed to update brief."}), 500


@briefs_bp.route("/briefs/<brief_id>/submit", methods=["POST"])
@jwt_required
@require_role("REPORTER")
def submit_brief_route(brief_id: str):
    try:
        uuid.UUID(brief_id)
    except ValueError:
        return jsonify({"error": "Invalid Format", "message": f"'{brief_id}' is not a valid UUID."}), 400

    try:
        submitted = submit_brief(brief_id, g.user["sub"])
        return jsonify({
            "status": "success",
            "message": "Brief draft submitted successfully for Editor review.",
            "brief": submitted
        }), 200
    except ValueError as ve:
        return jsonify({"error": "Workflow Error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "Database Error", "message": "Failed to submit brief."}), 500


@briefs_bp.route("/briefs/<brief_id>/publish", methods=["POST"])
@jwt_required
@require_role(["EDITOR"])
def publish_brief_route(brief_id: str):
    """
    CRITICAL WORKFLOW REQUIREMENT: Allowed ONLY for EDITOR role.
    Reporter or Desk Head attempting this route receives 403 Forbidden.
    """
    try:
        uuid.UUID(brief_id)
    except ValueError:
        return jsonify({"error": "Invalid Format", "message": f"'{brief_id}' is not a valid UUID."}), 400

    try:
        published = publish_brief(brief_id, g.user["sub"])
        return jsonify({
            "status": "success",
            "message": f"Brief published successfully by Editor {g.user['name']}.",
            "brief": published
        }), 200
    except ValueError as ve:
        return jsonify({"error": "Workflow Error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "Database Error", "message": "Failed to publish brief."}), 500
