from flask import Blueprint, request, jsonify
from decorators.jwt_required import jwt_required
from models.notifications_model import MessageNotificationModel
from sqlalchemy import or_

notification_bp = Blueprint(
    "notification",  __name__, url_prefix='/notifications')


@notification_bp.route("/get_unread_notifications", methods=["GET"])
@jwt_required
def get_notifications():
    """ 
    route to get unread notifications associated with user from DB
    """
    try:
        user_id = request.user.get("sub")
        print("User ID from token:", user_id, "Type:", type(user_id))
        print("Full request.user:", dict(request.user))  # See all JWT claims
        print("User ID from token:", user_id)

        if not user_id:
            return jsonify({"error": "User ID not found in token"}), 401

        notifications = MessageNotificationModel.query.filter(
            MessageNotificationModel.is_read == False
        ).filter(
            or_(
                MessageNotificationModel.receiver_id == user_id,
                MessageNotificationModel.sender_id == user_id
            )
        ).all()

        if len(notifications) < 1:
            return jsonify({
                "success": True,
                "notifications": [],
                "count": 0
            })

        notifications_data = [notification.to_dict()
                              for notification in notifications]

        return jsonify({
            "success": True,
            "notifications": notifications_data,
            "count": len(notifications_data)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
