from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from marshmallow import ValidationError
from extension import db
from modules.schemas.users_schema import LoginSchema, SignUpSchema
from user.user_model import User
from utils.jwt import generate_jwt_token

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=["POST"])
def register_user():
    try:
        schema = SignUpSchema()
        data = schema.load(request.get_json())
        username = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not username or not password or not email:
            return jsonify({"error": "Missing fields"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 409

        user = User(username=username)
        user.set_password(password)

        token_payload = {
            "sub": str(user.id),
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(seconds=current_app.config['JWT_EXPIRES_IN'])
        }
        access_token = generate_jwt_token(
            token_payload, current_app.config["JWT_ALGORITHM"],
            current_app.config["JWT_SECRET_KEY"])
        print(access_token)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully",
                        "access-token": str(access_token)}), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400


@auth_bp.route('/sign-in', methods=["GET"])
def me():
    return "We got here!!"
