from flask import Flask, request
from flask_cors import CORS
from config import Config
from routes.health import health_bp
from routes.auth import auth_bp
from routes.raw_items import raw_items_bp
from routes.stories import stories_bp
from routes.briefs import briefs_bp
from routes.merge import merge_bp
from routes.analytics import analytics_bp
from routes.rbac_test import rbac_test_bp
from routes.demo import demo_bp
from routes.errors import register_error_handlers


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for frontend integration across all API resources
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://news-brief-desk.vercel.app"
    ]
    if Config.CORS_ORIGINS:
        for orig in Config.CORS_ORIGINS:
            clean_orig = orig.strip().rstrip("/")
            if clean_orig and clean_orig not in allowed_origins:
                allowed_origins.append(clean_orig)

    CORS(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        if origin:
            clean_origin = origin.strip().rstrip("/")
            if clean_origin in allowed_origins or not Config.CORS_ORIGINS:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response

    # Register Blueprints
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(raw_items_bp, url_prefix="/api")
    app.register_blueprint(stories_bp, url_prefix="/api")
    app.register_blueprint(briefs_bp, url_prefix="/api")
    app.register_blueprint(merge_bp, url_prefix="/api")
    app.register_blueprint(analytics_bp, url_prefix="/api")
    app.register_blueprint(rbac_test_bp, url_prefix="/api")
    app.register_blueprint(demo_bp, url_prefix="/api")

    # Register Error Handlers
    register_error_handlers(app)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=Config.DEBUG,
    )
