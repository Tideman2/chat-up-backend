from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from marshmallow import ValidationError
from utils.jwt import generate_jwt_token
from models.user_model import User
from modules.schemas.auth_shema import GetTokenSchema
from modules.schemas.users_schema import SignUpSchema, LoginSchema
from services.user_service import UserService, UserServiceError

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# Get new token
@auth_bp.route("/get_token", methods=["POST"])
def get_new_token():
    schema = GetTokenSchema()
    data = schema.load(request.get_json())
    username = data.get("username")
    user_id = data.get("userId")
    print("I ran, in get new token end-point")

    if not User.query.filter_by(username=username).first():
        return jsonify({"error": "User not found"}), 404

    token_payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.utcnow() + timedelta(seconds=current_app.config["JWT_EXPIRES_IN"]),
    }

    access_token = generate_jwt_token(
        token_payload,
        current_app.config["JWT_ALGORITHM"],
        current_app.config["JWT_SECRET_KEY"],
    )
    print(access_token, "Token from get new token")

    return jsonify({"access-token": access_token}), 200


@auth_bp.route("/register", methods=["POST"])
def register_user():
    try:
        schema = SignUpSchema()
        data = schema.load(request.get_json())  # validate input
        access_token, user_identity = UserService.create_user(data)

        return jsonify({
            "message": "User registered successfully",
            "user-id": str(user_identity),
            "access-token": str(access_token),
            "status-code": int(201)
        }), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except UserServiceError as err:
        message, code = err.args
        return jsonify({"error": message}), code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login_user():
    try:
        schema = LoginSchema()
        data = schema.load(request.get_json())  # validate input
        access_token, user_identity = UserService.validate_user(data)

        return jsonify({
            "message": "User login successful",
            "access-token": str(access_token),
            "user-info": user_identity,
            "status-code": int(201)
        }), 200

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except UserServiceError as err:
        message, code = err.args
        return jsonify({"error": message}), code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
