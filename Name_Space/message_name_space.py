# sockets/message_namespace.py
from datetime import datetime
from flask_socketio import Namespace, emit, join_room, leave_room
from flask import request
from extension import db
from models.message_model import Message
from models.user_model import User


class MessageNamespace(Namespace):
    def on_connect(self):
        """Handle client connection"""
        print(f"Client {request.sid} connected to Message namespace")
        emit('connected', {'status': 'connected', 'sid': request.sid})

    def on_disconnect(self):
        """Handle client disconnection"""
        print(f"Client {request.sid} disconnected from Message namespace")

    def on_join_room(self, data):
        """Join a chat room"""
        room_id = data.get('room_id')
        user_id = data.get('user_id')

        if room_id and user_id:
            join_room(str(room_id))
            emit('room_joined', {'room_id': room_id, 'user_id': user_id})
            print(f"User {user_id} joined room {room_id}")

    def on_leave_room(self, data):
        """Leave a chat room"""
        room_id = data.get('room_id')
        user_id = data.get('user_id')

        if room_id and user_id:
            leave_room(str(room_id))
            emit('room_left', {'room_id': room_id, 'user_id': user_id})
            print(f"User {user_id} left room {room_id}")

    def on_join_user_room(self, data):
        """Join user's personal room for private messages"""
        user_id = data.get('user_id')
        if user_id:
            join_room(str(user_id))
            emit('user_room_joined', {'user_id': user_id})

    def on_private_message(self, data):
        """Handle private messages between users"""
        try:
            content = data.get('content')
            sender_id = data.get('sender_id')
            receiver_id = data.get('receiver_id')

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
