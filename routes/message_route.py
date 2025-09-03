from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from models.user_model import User
from decorators.jwt_required import jwt_required
from modules.schemas.message_schema import SentMessageSchema


message_bp = Blueprint('message', __name__, url_prefix='/message')


@message_bp.route('/send', methods=["POST"])
@jwt_required
def send_message():
    try:
        schema = SentMessageSchema()
        data = schema.load(request.get_json())
        print(data)
        return jsonify(data)  # URL: /message/send
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400


@message_bp.route('/inbox')
def get_inbox():
    return "inbox"
