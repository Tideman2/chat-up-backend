from flask_socketio import Namespace, emit
from marshmallow import ValidationError
from modules.schemas.users_schema import SignUpSchema, LoginSchema
from services.user_service import UserService, UserServiceError


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
