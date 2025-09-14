from flask_socketio import Namespace, emit
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from marshmallow import ValidationError
from utils.jwt import generate_jwt_token
from models.user_model import User
from modules.schemas.auth_shema import GetTokenSchema
from modules.schemas.users_schema import SignUpSchema, LoginSchema
from services.user_service import UserService, UserServiceError

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route("/get_token", methods=["POST"])
def get_new_token():
    schema = GetTokenSchema()
    print("i raannnnnn", request.get_json())
    data = schema.load(request.get_json())
    username = data.get("username")
    user_id = data.get("userId")

    if not User.query.filter_by(username=username).first():
        return jsonify({"error": "User not found"}, 404)

    token_payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.utcnow() + timedelta(seconds=current_app.config['JWT_EXPIRES_IN'])
    }

    access_token = generate_jwt_token(
        token_payload, current_app.config["JWT_ALGORITHM"],
        current_app.config["JWT_SECRET_KEY"])
    print(access_token, "Token from get new token")
    return jsonify({'access-token': access_token}, 200)


class AuthNamespace(Namespace):
    """
    Namespace for auth (signup/login) events.
    """

    def on_register_user(self, data):
        """
        Event: 'register_user'
        Client sends signup data -> server validates & creates user -> emit response.
        """
        try:
            schema = SignUpSchema()
            data = schema.load(data)
            service_data = UserService.create_user(data)
            access_token, user_identity = service_data
            response = {
                "message": "User registered successfully",
                "user-id": str(user_identity),
                "access-token": str(access_token),
                "status-code": 201
            }

            emit("register_user_response", response)

        except ValidationError as err:
            emit("register_user_response", {
                 "errors": err.messages, "status-code": 400})
        except UserServiceError as err:
            message, code = err.args
            emit("register_user_response", {
                 "error": message, "status-code": code})
        except Exception as e:  # fallback
            emit("register_user_error", {"error": str(e), "status-code": 500})

    def on_login_user(self, data):
        try:
            schema = LoginSchema()
            data = schema.load(data)
            service_data = UserService.validate_user(data)
            access_token, user_identity = service_data
            response = {"message": "User login successful",
                        "access-token": str(access_token),
                        "user-info": user_identity,
                        "status-code": 201}
            emit("login_user_response", response)

        except ValidationError as err:
            emit("login_user_response", {"errors": err.messages,
                                         "status-code": 400})
        except UserServiceError as err:
            message, code = err.args
            emit("login_user_response", {"errors": message,
                                         "status-code": code})
        except Exception as e:  # fallback
            emit("register_user_error", {"error": str(e), "status-code": 500})
