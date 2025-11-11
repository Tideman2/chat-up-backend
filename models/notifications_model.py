from datetime import datetime
from extension import db


class MessageNotificationModel(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    receiver_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Use distinct backref names to avoid ambiguity
    sender = db.relationship('User', foreign_keys=[sender_id],
                             backref='sent_notifications')  # Changed backref
    receiver = db.relationship('User', foreign_keys=[receiver_id],
                               backref='received_notifications')  # Changed backref
    room = db.relationship('Room', backref='notifications')

    def to_dict(self):

        return {
            'id': self.id,
            'senderId': self.sender_id,
            'receiverId': self.receiver_id,
            'roomId': self.room_id,
            'isRead': self.is_read,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
