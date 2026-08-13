from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required

from app import db
from detector.rules import is_login_rate_limited, record_failed_login
from models.user import User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def validate_password(password):
    if len(password) < 12:
        return "password must be at least 12 characters"
    if not any(character.islower() for character in password):
        return "password must include a lowercase letter"
    if not any(character.isupper() for character in password):
        return "password must include an uppercase letter"
    if not any(character.isdigit() for character in password):
        return "password must include a number"
    if not any(not character.isalnum() for character in password):
        return "password must include a symbol"
    return None


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({
            "error": "username, email and password are required"
        }), 400

    if "@" not in email:
        return jsonify({"error": "email must be valid"}), 400

    password_error = validate_password(password)
    if password_error:
        return jsonify({"error": password_error}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username already exists"}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already exists"}), 409

    user = User(
        username=username,
        email=email
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "user registered successfully",
        "user_id": user.id
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "email and password are required"
        }), 400

    if is_login_rate_limited(request.remote_addr):
        return jsonify({
            "error": "too many failed login attempts; try again later"
        }), 429

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        record_failed_login(email, request.remote_addr)
        return jsonify({
            "error": "invalid email or password"
        }), 401

    login_user(user)

    return jsonify({
        "message": "login successful",
        "user_id": user.id,
        "username": user.username
    })


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()

    return jsonify({
        "message": "logout successful"
    })
