from datetime import datetime, timezone
from flask_socketio import Namespace, emit, join_room, leave_room
from flask import request
from extension import db
from models.message_model import Message, Room, RoomMember
from models.user_model import User


class MessageNamespace(Namespace):

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
        print(f"Client {request.sid} connected to Message namespace")
        emit('connected', {'status': 'connected', 'sid': request.sid})

    def on_disconnect(self):
        """Handle client disconnection"""
        print(f"Client {request.sid} disconnected from Message namespace")

    def on_echo_test(self, data):
        print("Echo test received", data)
        emit("echo_response", {"echo": data,
             "timestamp": datetime.now().isoformat()})

    def on_entry_to_private_dm(self, data):
        """User wants to enter a private DM conversation"""
        try:
            sender_id = data.get('userId')
            receiver_id = data.get('receiverId')
            print("Data received in entry to private dm:", data)

            if not all([sender_id, receiver_id]):
                emit('error', {'message': 'Missing user IDs'})
                return

            # Get or create the private room
            room = self._get_or_create_private_room(sender_id, receiver_id)

            # Join the room
            join_room(room.name)
            print(f"User {sender_id} joined room {room.name}")

            # Get all messages in this room
            messages = Message.query.filter_by(room_id=room.id)\
                .order_by(Message.timestamp.asc())\
                .all()

            # Prepare messages data
            messages_data = []
            for msg in messages:
                sender = User.query.get(msg.sender_id)
                messages_data.append({
                    'id': msg.id,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat(),
                    'sender_id': msg.sender_id,
                    'sender_username': sender.username if sender else 'Unknown',
                    'receiver_id': msg.receiver_id,
                    'room_id': msg.room_id,
                    'type': 'private'
                })

            response = {
                "senderId": sender_id,
                "receiverId": receiver_id,
                "roomName": room.name,
                "roomId": room.id,
                "existingRoom": True,
                "messages": messages_data
            }

            emit("entry_to_dm_response", response)
            print(f"Sent {len(messages_data)} messages to user {sender_id}")

        except Exception as e:
            print(f"Error in entry_to_private_dm: {str(e)}")
            emit('error', {'message': f'Failed to enter DM: {str(e)}'})

    def on_private_message(self, data):
        """Handle private messages between users using room-based approach"""
        try:
            content = data.get('content')
            sender_id = data.get('sender_id')
            receiver_id = data.get('receiver_id')

            if not all([content, sender_id, receiver_id]):
                emit('error', {'message': 'Missing required fields'})
                return

            print("Private message data received:", data)

            # Get or create the private room
            room = self._get_or_create_private_room(sender_id, receiver_id)

            # Create new message associated with the room
            message = Message(
                content=content,
                sender_id=sender_id,
                receiver_id=receiver_id,
                room_id=room.id,  # Critical: Associate with room
                timestamp=datetime.now(timezone.utc)
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
                'sender_username': sender.username if sender else 'Unknown',
                'receiver_id': message.receiver_id,
                'room_id': message.room_id,
                'type': 'private'
            }

            # Emit to everyone in the room (both users)
            emit('new_message', message_data, room=room.name)
            print(f"Message sent to room {room.name}")

        except Exception as e:
            print(f"Error in private_message: {str(e)}")
            emit('error', {'message': f'Failed to send message: {str(e)}'})
            db.session.rollback()

    def on_get_private_messages(self, data):
        """Get historical private messages between users"""
        try:
            user1_id = data.get('user1_id')
            user2_id = data.get('user2_id')
            limit = data.get('limit', 50)
            offset = data.get('offset', 0)

            if not all([user1_id, user2_id]):
                emit('error', {'message': 'Missing user IDs'})
                return

            # Get the private room
            room = self._get_or_create_private_room(user1_id, user2_id)

            # Get messages from this specific room
            messages = Message.query.filter_by(room_id=room.id)\
                .order_by(Message.timestamp.asc())\
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
                    'sender_username': sender.username if sender else 'Unknown',
                    'receiver_id': message.receiver_id,
                    'room_id': message.room_id,
                    'type': 'private'
                })

            emit('private_messages', {
                 'messages': messages_data, 'room_id': room.id})

        except Exception as e:
            print(f"Error in get_private_messages: {str(e)}")
            emit(
                'error', {'message': f'Failed to get private messages: {str(e)}'})
