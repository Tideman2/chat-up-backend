from werkzeug.security import generate_password_hash, check_password_hash
from extension import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(500), nullable=False)
    profile_image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # relationships
    messages_sent = db.relationship(
        'Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    room_memberships = db.relationship(
        'RoomMember', back_populates='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_user_identity(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
        }
