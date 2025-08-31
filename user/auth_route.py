from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from models.user_model import User
from modules.schemas.users_schema import LoginSchema, SignUpSchema
from services.user_service import UserService, UserServiceError

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=["POST"])
def register_user():
    try:
        schema = SignUpSchema()
        data = schema.load(request.get_json())
        access_token = UserService.create_user(data)
        return jsonify({"message": "User registered successfully",
                        "access-token": str(access_token)}), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except UserServiceError as err:
        message, code = err.args
        return jsonify({"error": message}), code


@auth_bp.route('/sign-in', methods=["POST"])
def login_user():
    try:
        schema = LoginSchema()
        data = schema.load(request.get_json())
        access_token = UserService.validate_user(data)
        return jsonify({"message": "User login successful",
                        "access-token": str(access_token)}), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except UserServiceError as err:
        message, code = err.args
        return jsonify({"error": message}), code
