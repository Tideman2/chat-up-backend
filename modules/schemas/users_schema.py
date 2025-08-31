from flask import Flask, request, jsonify
from marshmallow import Schema, fields
from marshmallow.validate import Email


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class SignUpSchema(Schema):
    name = fields.Str(required=True)
    password = fields.Str(required=True)
    email = fields.Str(required=True, validate=Email(
        error="Invalid email address"))
