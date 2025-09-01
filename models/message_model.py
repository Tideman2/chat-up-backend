from datetime import datetime
from extension import db


class Message(db.Model):
    """
    A class model for user messages and
    it's also a many to one relationship with the User table

    """

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('chat_room.id'))
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(
        db.DateTime, default=datetime.now(datetime.timezone.utc))
    is_read = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', foreign_keys=[sender_id])


class ChatRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))  # Only for groups
    is_group = db.Column(db.Boolean, default=False)


class ChatRoomUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('chat_room.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
