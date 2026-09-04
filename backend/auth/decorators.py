from functools import wraps
from typing import List, Union
from flask import request, jsonify, g
from auth.jwt import decode_access_token


def jwt_required(f):
    """
    Decorator requiring a valid JWT Bearer token in the Authorization header.
    Attaches authenticated payload to Flask's request context g.user.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({
                "error": "Authentication required",
                "message": "Authorization header is missing."
            }), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({
                "error": "Authentication required",
                "message": "Authorization header must follow format: Bearer <token>"
            }), 401

        token = parts[1]
        payload = decode_access_token(token)
        if not payload:
            return jsonify({
                "error": "Authentication required",
                "message": "Invalid or expired access token."
            }), 401

        g.user = payload
        return f(*args, **kwargs)

    return decorated_function


def require_role(roles: Union[str, List[str]]):
    """
    Decorator enforcing Role-Based Access Control (RBAC).
    Must be placed after @jwt_required or will automatically check g.user.
    """
    if isinstance(roles, str):
        allowed_roles = [roles]
    else:
        allowed_roles = list(roles)

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, "user") or not g.user:
                return jsonify({
                    "error": "Authentication required",
                    "message": "User session not authenticated."
                }), 401

            user_role = g.user.get("role")
            if user_role not in allowed_roles:
                return jsonify({
                    "error": "Insufficient permissions",
                    "message": f"Role '{user_role}' is not authorized to access this resource."
                }), 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator
