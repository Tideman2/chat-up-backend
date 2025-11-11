import os
from flask_migrate import Migrate
from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv
from flask_cors import CORS
from extension import db
from models.user_model import User
from models.message_model import Message, RoomMember, Room
# from routes.auth_route import AuthNamespace
from Name_Space.message_name_space import MessageNamespace
from Name_Space.message_notification_space import MessageNotificationNameSpace
from routes.user_route import user_bp


cors = CORS()
migrate = Migrate()
socketio = SocketIO()


def create_app() -> Flask:
    """
    Creates and configures a Flask application instance.

    Initializes:
    - Database (SQLAlchemy)
    - CORS
    - JWT settings
    - Registration of name_space

    Returns:
        Flask: The configured Flask application instance.
    """
    load_dotenv()

    app = Flask(__name__)

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/project_images'

    # JWT config
    app.config['JWT_SECRET_KEY'] = os.environ.get(
        "JWT_SECRET_KEY", "dev-secret")
    app.config['JWT_ALGORITHM'] = os.environ.get("JWT_ALGORITHM", "HS256")
    app.config['JWT_EXPIRES_IN'] = int(
        os.environ.get("JWT_EXPIRES_IN", 3600))  # Added default

    # Initialize extensions
    db.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins=["http://localhost:5173",
                                                 "http://localhost:5174"])

    # register name_space
    # socketio.on_namespace(AuthNamespace("/auth"))
    socketio.on_namespace(MessageNamespace("/message"))
    socketio.on_namespace(
        MessageNotificationNameSpace("/message-notification"))
    return app
