from flask import current_app
from datetime import datetime, timedelta
from extension import db
from models.user_model import User
from utils.jwt import generate_jwt_token


class UserServiceError(Exception):
    pass


class UserService:
    """
    A class to handle user create and validation logics
    errors are raised from these methods that are exempted in auth_route.py

    """

    @staticmethod
    def create_user(data):
        username = data.get("name")
        email = data.get("email")
        password = data.get("password")
        print(data, "daraa")
        if not username or not password or not email:
            raise UserServiceError(("Missing fields"), 400)
        if User.query.filter_by(username=username).first():
            raise UserServiceError(("Username already exist"), 401)

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("Db in userService commit failed:", e)
            raise

        token_payload = {
            "sub": str(user.id),
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(seconds=current_app.config['JWT_EXPIRES_IN'])
        }
        access_token = generate_jwt_token(
            token_payload, current_app.config["JWT_ALGORITHM"],
            current_app.config["JWT_SECRET_KEY"])
        print(access_token)
        data = [access_token, user.get_user_identity()]
        return data

    @staticmethod
    def validate_user(data):
        username = data.get("username")
        password = data.get("password")
        user = User.query.filter_by(username=username).first()

        if not user:
            raise UserServiceError(("Username does not exist"), 401)

        if not user.check_password(password=password):
            raise UserServiceError(("Password is wrong"), 401)

        token_payload = {
            "sub": str(user.id),
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(seconds=current_app.config['JWT_EXPIRES_IN'])
        }
        access_token = generate_jwt_token(
            token_payload, current_app.config["JWT_ALGORITHM"],
            current_app.config["JWT_SECRET_KEY"])

        data = [access_token, user.get_user_identity()]
        return data
