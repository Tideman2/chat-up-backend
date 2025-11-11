from marshmallow import Schema, fields


class SentMessageSchema(Schema):
    content = fields.Str(required=True)
    sender_id = fields.Str(required=True)
    receiver_id = fields.Str(required=False)
    room_id = fields.Str(required=False)
