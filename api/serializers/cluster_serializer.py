from marshmallow import fields, ValidationError
from nails import Serializer

class ClusterSerializer(Serializer):
    provider = fields.Str()

class AwsClusterSerializer(ClusterSerializer):
    pass
