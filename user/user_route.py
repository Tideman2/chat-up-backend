from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from extension import db
from modules.schemas.users_schema import LoginSchema, SignUpSchema
from user.user_model import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=["POST"])
def register_user():
    try:
        schema = LoginSchema()
        data = schema.load(request.get_json())
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not password or not email:
            return jsonify({"error": "Missing fields"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 409

        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400


@auth_bp.route('/sign-in', methods=["GET"])
def me():
    return "We got here!!"
