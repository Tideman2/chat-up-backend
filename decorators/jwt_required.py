import jwt
from utils.jwt import decode_jwt_token
from flask import request, jsonify, current_app
from functools import wraps


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return jsonify({"error": "Missing Authorization header"}), 401

            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Invalid Authorization format"}), 401

            token = auth_header.split(" ")[1]
            if not token:
                return jsonify({"error": "Empty token"}), 401

            print(f"Attempting to decode token:...")

            decoded = decode_jwt_token(
                token,
                current_app.config["JWT_ALGORITHM"],
                current_app.config["JWT_SECRET_KEY"]
            )
            print(f"Decoded successfully")
            request.user = decoded

        except jwt.ExpiredSignatureError as e:
            print(f"Token expired: {e}")
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            print(f"Invalid token details: {e}")
            return jsonify({"error": f"Invalid token: {str(e)}"}), 401

        return f(*args, **kwargs)

    return decorated

# def jwt_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth_header = request.headers.get("Authorization")
#         if not auth_header or not auth_header.startswith("Bearer "):
#             return jsonify({"error": "Missing or invalid Authorization header"}), 401

#         token = auth_header.split(" ")[1]
#         print(token, "In JWt required")
#         try:
#             decoded = decode_jwt_token(
#                 token,
#                 current_app.config["JWT_ALGORITHM"],
#                 current_app.config["JWT_SECRET_KEY"]
#             )
#             request.user = decoded  # attach decoded user data to the request
#         except jwt.ExpiredSignatureError as e:
#             print("Invalid token error details:", e)
#             print("Token:", token)
#             return jsonify({"error": "Token has expired"}), 401
#         except jwt.InvalidTokenError as e:
#             print("Invalid token error details:", e)
#             print("Token:", token)
#             return jsonify({"error": "Token has expired"}), 401

#         return f(*args, **kwargs)

#     return decorated
