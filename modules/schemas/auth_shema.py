from marshmallow import Schema, fields, validates_schema, ValidationError


class GetTokenSchema(Schema):
    username = fields.Str(required=True)
    userId = fields.Str(required=True)
