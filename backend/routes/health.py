import os
from flask import Blueprint, jsonify
from db.connection import check_db_health

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    db_ok = check_db_health()
    status_code = 200 if db_ok else 503

    return jsonify({
        "status": "ok" if db_ok else "degraded",
        "service": "news-brief-desk-api",
        "database": "connected" if db_ok else "disconnected",
        "environment": os.getenv("FLASK_ENV", "development"),
    }), status_code


@health_bp.route("", methods=["GET"])
def api_root():
    return jsonify({
        "name": "News Brief Desk API",
        "version": "0.1.0",
        "phase": "Phase 1 - Database & Synthetic Dataset Foundation",
        "endpoints": [
            "/api/health",
            "/api/raw-items",
            "/api/raw-items/<id>",
            "/api/stats/raw-items"
        ]
    })
