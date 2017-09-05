from marshmallow import fields, post_load, ValidationError
from nails import Serializer

class UpdateUserSerializer(Serializer):
    id = fields.Field(required=True)
    first_name = fields.Str()
    last_name = fields.Str()
    display_name = fields.Str()
    username = fields.Str()
    email = fields.Email()
    password = fields.Str()

class GetUserSerializer(Serializer):
    id = fields.Field()
    username = fields.Str()
    email = fields.Email()

    @post_load
    def post_load(self, data):
        if (not 'id' in data) and (not 'email' in data):
            raise ValidationError('Missing data for required \'email\' or \'id\' field', data)

class UserSerializer(Serializer):
    id = fields.Field()
    username = fields.Str()
    email = fields.Str()
