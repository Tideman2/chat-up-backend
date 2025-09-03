from marshmallow import Schema, fields, validates_schema, ValidationError


class SentMessageSchema(Schema):
    content = fields.Str(required=True)
    sender_id = fields.Str(required=True)
    receiver_id = fields.Str(required=False)
    room_id = fields.Str(required=False)

    @validates_schema
    def validate_either_receiver_or_room(self, data, **kwargs):
        receiver_id = data.get('receiver_id')
        room_id = data.get('room_id')

        # Check if both are missing
        if receiver_id is None and room_id is None:
            raise ValidationError({
                'receiver_id': ['Either receiver_id or room_id must be provided'],
                'room_id': ['Either receiver_id or room_id must be provided']
            })

        # Check if both are provided
        if receiver_id is not None and room_id is not None:
            raise ValidationError({
                'receiver_id': ['Only one of receiver_id or room_id can be provided'],
                'room_id': ['Only one of receiver_id or room_id can be provided']
            })
