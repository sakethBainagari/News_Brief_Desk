from flask import Blueprint, request, jsonify, g
from db.queries import get_user_by_email, get_user_by_id
from auth.password import verify_password
from auth.jwt import generate_access_token
from auth.decorators import jwt_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({
            "error": "Bad Request",
            "message": "Request payload must be valid JSON."
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "Bad Request",
            "message": "Both 'email' and 'password' are required fields."
        }), 400

    user = get_user_by_email(email)
    if not user or not user.get("password_hash") or not verify_password(password, user["password_hash"]):
        return jsonify({
            "error": "Invalid credentials",
            "message": "The provided email or password is incorrect."
        }), 401

    access_token = generate_access_token(user)

    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }), 200


@auth_bp.route("/auth/me", methods=["GET"])
@jwt_required
def get_me():
    user_id = g.user.get("sub")
    user = get_user_by_id(user_id) if user_id else None

    if not user:
        return jsonify({
            "id": g.user.get("sub"),
            "name": g.user.get("name"),
            "email": g.user.get("email"),
            "role": g.user.get("role")
        }), 200

    return jsonify({
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"]
    }), 200
