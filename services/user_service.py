from flask import current_app
from datetime import datetime, timedelta
from extension import db
from models.user_model import User
from utils.jwt import generate_jwt_token


class UserServiceError(Exception):
    pass


class UserService:
    @staticmethod
    def create_user(data):
        username = data.get("name")
        email = data.get("email")
        password = data.get("password")
        print(data)

        if not username or not password or not email:
            raise UserServiceError(("Missing fields"), 400)
        if User.query.filter_by(username=username).first():
            raise UserServiceError(("Username already exist"), 401)

        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        token_payload = {
            "sub": str(user.id),
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(seconds=current_app.config['JWT_EXPIRES_IN'])
        }
        access_token = generate_jwt_token(
            token_payload, current_app.config["JWT_ALGORITHM"],
            current_app.config["JWT_SECRET_KEY"])
        print(access_token)
        return access_token
