from datetime import datetime
from extension import db


class Message(db.Model):
    """
    # Purpose: Stores chat messages.
    # Expected use: Can store messages for direct (1-to-1) or group chats.
    # If `receiver_id` is filled, it's a private message otherwise it's a group message.

    """
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    sender_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True)

    room = db.relationship('Room', back_populates='messages')


class Room(db.Model):
    """
    Purpose: Represents a chat group.
    Expected use: Store info about chat groups and link to messages and members.

    """
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_group = db.Column(db.Boolean, default=False)

    members = db.relationship('RoomMember', back_populates='room', lazy=True)
    messages = db.relationship('Message', back_populates='room', lazy=True)


class RoomMember(db.Model):
    """
    Purpose: Handles the many-to-many relationship between users and rooms.
    Expected use: Store which users belong to which groups.

    """
    __tablename__ = 'room_memberships'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='room_memberships')
    room = db.relationship('Room', back_populates='members')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'room_id', name='unique_membership'),
    )
