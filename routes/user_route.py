from flask import Blueprint, request, jsonify
from models.user_model import User
from decorators.jwt_required import jwt_required
import jwt

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route("/get_users", methods=["GET"])
@jwt_required
def get_users():
    try:
        print("Headers:", request.headers)
        all_users = User.query.all()
        users = [user.get_user_identity() for user in all_users]

        return jsonify(users), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401

    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    except Exception as e:
        # Catch anything unexpected
        return jsonify({"error": str(e)}), 500
