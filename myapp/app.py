import os
from flask_migrate import Migrate
from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from extension import db


cors = CORS()
migrate = Migrate()


def create_app() -> Flask:
    """
    Creates and configures a Flask application instance.

    Initializes:
    - Database (SQLAlchemy)
    - CORS
    - JWT settings

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

    return app
