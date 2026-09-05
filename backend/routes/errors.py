from flask import jsonify


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad Request",
            "message": str(error.description) if hasattr(error, "description") else "Invalid request payload or parameters."
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not Found",
            "message": "The requested API resource or endpoint does not exist."
        }), 404

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "error": "Authentication required",
            "message": str(error.description) if hasattr(error, "description") else "Authorization header is missing or invalid."
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "error": "Insufficient permissions",
            "message": str(error.description) if hasattr(error, "description") else "Forbidden resource."
        }), 403

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred on the server."
        }), 500
