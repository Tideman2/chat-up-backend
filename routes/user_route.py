from flask import Blueprint, request, jsonify
from models.user_model import User
from decorators.jwt_required import jwt_required


user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route("/get_users", methods=["GET"])
@jwt_required
def get_users():
    all_users = User.query.all()
    users = []

    for user in all_users:
        users.append(user.get_user_identity())

    return jsonify(users), 200
