import uuid
from flask import Blueprint, jsonify, request
from auth.decorators import jwt_required, require_role
from services.story_clustering import StoryClusteringEngine
from db.story_queries import get_story_clusters, get_story_cluster_by_id

stories_bp = Blueprint("stories", __name__)


@stories_bp.route("/stories/cluster", methods=["POST"])
@jwt_required
@require_role("REPORTER")
def run_event_clustering():
    """Triggers the 2-stage AI Event Grouping pipeline (Embeddings + FAISS + Gemini Verification + Graph Clustering)."""
    try:
        engine = StoryClusteringEngine()
        res = engine.process_and_cluster(save_to_db=True)
        return jsonify({
            "status": "success",
            "message": f"Successfully clustered {res['total_items']} raw news items into {res['total_clusters']} story clusters.",
            "data": res
        }), 200
    except BaseException as e:
        return jsonify({
            "error": "Clustering Error",
            "message": f"Failed to execute story clustering pipeline: {str(e)}"
        }), 500


@stories_bp.route("/stories", methods=["GET"])
@jwt_required
def list_stories():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 50))
    except ValueError:
        return jsonify({
            "error": "Invalid Parameters",
            "message": "'page' and 'limit' must be integers."
        }), 400

    try:
        res = get_story_clusters(page=page, limit=limit)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({
            "error": "Database Query Error",
            "message": "Unable to retrieve story clusters."
        }), 500


@stories_bp.route("/stories/<story_id>", methods=["GET"])
@jwt_required
def get_story_detail(story_id: str):
    try:
        uuid.UUID(story_id)
    except ValueError:
        return jsonify({
            "error": "Invalid Format",
            "message": f"'{story_id}' is not a valid UUID."
        }), 400

    try:
        cluster = get_story_cluster_by_id(story_id)
        if not cluster:
            return jsonify({
                "error": "Not Found",
                "message": f"Story cluster with ID '{story_id}' was not found."
            }), 404
        return jsonify(cluster), 200
    except Exception as e:
        return jsonify({
            "error": "Database Query Error",
            "message": "Unable to retrieve story cluster details."
        }), 500


@stories_bp.route("/stories/<story_id>/sources", methods=["GET"])
@jwt_required
def get_story_sources(story_id: str):
    try:
        uuid.UUID(story_id)
    except ValueError:
        return jsonify({
            "error": "Invalid Format",
            "message": f"'{story_id}' is not a valid UUID."
        }), 400

    try:
        cluster = get_story_cluster_by_id(story_id)
        if not cluster:
            return jsonify({
                "error": "Not Found",
                "message": f"Story cluster with ID '{story_id}' was not found."
            }), 404
        return jsonify({
            "story_id": story_id,
            "canonical_headline": cluster["canonical_headline"],
            "source_count": cluster["source_count"],
            "sources": cluster["sources"]
        }), 200
    except Exception as e:
        return jsonify({
            "error": "Database Query Error",
            "message": "Unable to retrieve story sources."
        }), 500
