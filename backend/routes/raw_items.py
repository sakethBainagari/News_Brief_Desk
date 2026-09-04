import uuid
from flask import Blueprint, jsonify, request
from db.queries import get_raw_items, get_raw_item_by_id, get_raw_items_stats
from auth.decorators import jwt_required, require_role

raw_items_bp = Blueprint("raw_items", __name__)


@raw_items_bp.route("/raw-items", methods=["GET"])
@jwt_required
@require_role("REPORTER")
def list_raw_items():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return jsonify({
            "error": "Invalid pagination parameters",
            "message": "'page' and 'limit' must be integers."
        }), 400

    if page < 1 or limit < 1:
        return jsonify({
            "error": "Invalid pagination parameters",
            "message": "'page' and 'limit' must be positive integers."
        }), 400

    limit = min(limit, 100)

    category = request.args.get("category")
    source = request.args.get("source")
    search = request.args.get("search")

    try:
        res = get_raw_items(
            page=page,
            limit=limit,
            category=category,
            source=source,
            search=search
        )
        return jsonify(res), 200
    except Exception as e:
        return jsonify({
            "error": "Database Query Error",
            "message": "Unable to retrieve raw items. Verify database connection."
        }), 500


@raw_items_bp.route("/raw-items/<item_id>", methods=["GET"])
@jwt_required
@require_role("REPORTER")
def get_raw_item(item_id: str):
    try:
        uuid.UUID(item_id)
    except ValueError:
        return jsonify({
            "error": "Invalid Format",
            "message": f"'{item_id}' is not a valid UUID."
        }), 400

    try:
        item = get_raw_item_by_id(item_id)
        if not item:
            return jsonify({
                "error": "Not Found",
                "message": f"Raw news item with ID '{item_id}' was not found."
            }), 404
        return jsonify(item), 200
    except Exception as e:
        return jsonify({
            "error": "Database Query Error",
            "message": "Unable to retrieve item detail."
        }), 500


@raw_items_bp.route("/stats/raw-items", methods=["GET"])
@jwt_required
@require_role("REPORTER")
def raw_items_stats():
    try:
        stats = get_raw_items_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({
            "error": "Database Query Error",
            "message": "Unable to calculate raw items statistics."
        }), 500
