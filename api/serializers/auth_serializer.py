from marshmallow import fields, ValidationError
from nails import Serializer

class RegisterSerializer(Serializer):
    first_name = fields.Str()
    last_name = fields.Str()
    display_name = fields.Str()
    username = fields.Str()
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UpdateAuthedUserSerializer(Serializer):
    email = fields.Email()
    password = fields.Str()
    role = fields.Str()

class GitHubCallbackSerializer(Serializer):
    access_token = fields.Str(required=True)
    scope = fields.Str(required=True)
    token_type = fields.Str(required=True)
