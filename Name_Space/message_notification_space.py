from datetime import datetime, timezone
from flask_socketio import Namespace, emit, join_room, leave_room
from flask import request
from extension import db
from models.message_model import Message, Room, RoomMember
from models.user_model import User
from models.notifications_model import MessageNotificationModel


class MessageNotificationNameSpace(Namespace):
    """
    A name space to handle creation, saving and sending of notifications
    """

    def _get_or_create_private_room(self, user1_id, user2_id):
        """Helper method to find or create a private room for two users"""
        # Find existing room with exactly these two members
        room = (
            Room.query
            .join(RoomMember)
            .filter(Room.is_group.is_(False))
            .group_by(Room.id)
            .having(db.func.count(RoomMember.user_id) == 2)
            .filter(Room.members.any(RoomMember.user_id == user1_id))
            .filter(Room.members.any(RoomMember.user_id == user2_id))
            .first()
        )

        if room:
            print(f"Found existing private room: {room.name}")
            return room
        else:
            # Create new room
            lower_id = min(int(user1_id), int(user2_id))
            higher_id = max(int(user1_id), int(user2_id))
            room_name = f"{lower_id}_{higher_id}"

            room = Room(name=room_name, is_group=False)
            db.session.add(room)
            db.session.flush()  # Get room ID without committing

            # Add both users as members
            room.members.append(RoomMember(user_id=user1_id))
            room.members.append(RoomMember(user_id=user2_id))
            db.session.commit()
            print(f"Created new private room: {room_name}")
            return room

    def on_connect(self):
        """Handle client connection"""
        print(
            f"Client {request.sid} connected to Message_Notification namespace")

        emit('connected', {'status': 'connected', 'sid': request.sid})

    def on_disconnect(self):
        """Handle client disconnection"""
        print(
            f"Client {request.sid} disconnected from Message_Notification namespace")

    def on_tests_socket(self):
        """
         To test notification namespace
        """
        print("Test on Notifications is working")

    def on_notifications_room(self, data):
        """
         To join user rooms betwween user and friends
        """

        print("Test on Notifications is working")
        try:
            sender_id = data.get('senderId')
            receiver_id = data.get('receiverId')
            print("we goot here", sender_id, receiver_id)
            if not all([sender_id, receiver_id]):
                emit('error', {'message': 'Missing user IDs'})
                return
            print("what about here")
            room = self._get_or_create_private_room(sender_id, receiver_id)

            # Join the room
            print("About room joined")
            join_room(room.name)
            print("Room name: ", room.name)
            emit("join_notification_room_name", room.name)

        except Exception as e:
            print(f"Error in private_message: {str(e)}")
            emit(
                'error', {'message_notification': f'Failed to create notification: {str(e)}'})
            db.session.rollback()

    def on_create_notification(self, data):
        "create notification and save to data-base"
        print("create notification and save to data-base")
        try:
            sender_id = data.get("senderId")
            receiver_id = data.get("recieverId")
            room_id = data.get("roomId")

            if not all([sender_id, receiver_id, room_id]):
                emit(
                    'error', {'messageNotification event': 'Missing required fields'})
                return
            print("we got herrrree")
            notification = MessageNotificationModel(
                sender_id=sender_id, receiver_id=receiver_id, room_id=room_id)

            db.session.add(notification)
            db.session.commit()
            print("what about here")
            # construct response
            message_notification = {
                "notificationId": notification.id,
                "roomId": notification.room_id,
                "senderId": notification.sender_id,
                "recieverId": notification.receiver_id,
                "isRead": notification.is_read,
            }
            room = self._get_or_create_private_room(sender_id, receiver_id)

            emit('new_message_notification',
                 message_notification, room=room.name)

        except Exception as e:
            print(f"Error in private_message: {str(e)}")
            emit(
                'error', {'message_notification': f'Failed to create notification: {str(e)}'})
            db.session.rollback()


def on_set_notification_as_read(self, data):
    """
    SET NOTIFICATION AS READ IN DB
    """
    try:
        notification_id = data.get("notificationId")
        # Find the notification
        notification = MessageNotificationModel.query.get(notification_id)

        if notification:
            # Update is_read to True
            notification.is_read = True
            db.session.commit()

            emit('notification_read', {
                'notificationId': notification_id,
                'status': 'read'
            })
        else:
            emit('error', {'message': 'Notification not found'})

    except Exception as e:
        print(f"Error setting notification as read: {str(e)}")
        emit('error', {'message': f'Failed to update notification: {str(e)}'})
        db.session.rollback()
