# sockets/message_namespace.py
from datetime import datetime
from sqlalchemy import func
from flask_socketio import Namespace, emit, join_room, leave_room
from flask import request
from extension import db
from models.message_model import Message, Room, RoomMember
from models.user_model import User


class MessageNamespace(Namespace):
    def on_connect(self):
        """Handle client connection"""
        print(f"Client {request.sid} connected to Message namespace")
        emit('connected', {'status': 'connected', 'sid': request.sid})

    def on_disconnect(self):
        """Handle client disconnection"""
        print(f"Client {request.sid} disconnected from Message namespace")

    def on_entry_to_private_dm(self, data):
        """
        Check if there is a room with only both users as members
        if it exists get the messages in the room and return the messsages
        if it does not exist create a room and membership for both users
        room name should be concanation of both users id

        """
        sender_id = data.get('userId')
        receiver_id = data.get('receiverId')

        room = (
            Room.query
            .join(RoomMember)
            .filter(Room.is_group.is_(False))
            .group_by(Room.id)
            .having(db.func.count(RoomMember.user_id) == 2)
            .filter(Room.members.any(RoomMember.user_id == sender_id))
            .filter(Room.members.any(RoomMember.user_id == receiver_id))
            .first()
        )

        if room:  # access all messages of that room
            for msg in room.messages:
                print(msg.content, msg.timestamp)
        else:
            # create room
            # create room_memberships for both users
            # Join flask_socketIo room
            lower_id = min(int(sender_id), int(receiver_id))
            higher_id = max(int(sender_id), int(receiver_id))
            room_name = f"{lower_id}_{higher_id}"

            join_room(room_name)
            room = Room(name=room_name, is_group=False)
            db.session.add(room)
            db.session.flush()

            # Add memberships
            room.members.append(RoomMember(user_id=sender_id))
            room.members.append(RoomMember(user_id=receiver_id))
            response = {
                "senderId": sender_id,
                "receiverId": receiver_id,
                "roomName": room_name
            }

            emit("entry_to_dm_response", response)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("Db in userService commit failed:", e)
                raise

    def on_private_message(self, data):
        """Handle private messages between users"""
        try:
            content = data.get('content')
            sender_id = data.get('sender_id')
            receiver_id = data.get('receiver_id')
            room_id = data.get('room_id')

            if not all([content, sender_id, receiver_id]):
                emit('error', {'message': 'Missing required fields'})
                return

            # Create new message
            message = Message(
                content=content,
                sender_id=sender_id,
                receiver_id=receiver_id,
                timestamp=datetime.now(datetime.timezone.utc)
            )

            db.session.add(message)
            db.session.commit()

            # Get sender info
            sender = User.query.get(sender_id)

            # Prepare message data
            message_data = {
                'id': message.id,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'sender_id': message.sender_id,
                'receiver_id': message.receiver_id,
                'sender_username': sender.username,
                'type': 'private'
            }

            # Emit to sender
            emit('new_message', message_data, room=request.sid)

            # Emit to receiver (using user_id as room)
            emit('new_message', message_data, room=str(receiver_id))

        except Exception as e:
            emit('error', {'message': f'Failed to send message: {str(e)}'})
            db.session.rollback()

    def on_get_private_messages(self, data):
        """Get historical private messages between users"""
        try:
            user1_id = data.get('user1_id')
            user2_id = data.get('user2_id')
            limit = data.get('limit', 50)
            offset = data.get('offset', 0)

            messages = Message.query.filter(
                ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
                ((Message.sender_id == user2_id) &
                 (Message.receiver_id == user1_id))
            ).order_by(Message.timestamp.asc())\
             .offset(offset)\
             .limit(limit)\
             .all()

            messages_data = []
            for message in messages:
                sender = User.query.get(message.sender_id)
                messages_data.append({
                    'id': message.id,
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat(),
                    'sender_id': message.sender_id,
                    'sender_username': sender.username,
                    'receiver_id': message.receiver_id,
                    'type': 'private'
                })

            emit('private_messages', {'messages': messages_data})

        except Exception as e:
            emit(
                'error', {'message': f'Failed to get private messages: {str(e)}'})
