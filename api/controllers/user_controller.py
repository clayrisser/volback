from api.services import user_service
from api.serializers.user_serializer import (
    UpdateUserSerializer,
    GetUserSerializer,
    UserSerializer
)
from api.policies import is_authed, is_admin
from flask import jsonify, request
from nails import Controller
from playhouse.shortcuts import model_to_dict

class UserInstance(Controller):
    method_decorators = [is_authed]

    @is_admin
    def put(self):
        data, err = UpdateUserSerializer().load(request.json)
        user = user_service.update(data['id'], data)
        return jsonify(UserSerializer.load(model_to_dict(user))[0])

    def get(self):
        data, err = GetUserSerializer().load(request.args.to_dict())
        user = user_service.find_one(data)
        return jsonify(UserSerializer().load(model_to_dict(user))[0])

class UserList(Controller):
    def get(self):
        self.method_decorators = [is_authed, is_admin]
        return 'a list of users'
