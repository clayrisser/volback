from api.exceptions.user_exceptions import UserNotFound
from api.models import User
from api.services import auth_service
from flask import jsonify, request, abort
from nails import Controller
from nails.exceptions import Forbidden
from playhouse.shortcuts import model_to_dict

class UserInstance(Controller):
    def post(self):
        email = request.json.get('email')
        password = request.json.get('password')
        if User.select().where(User.email == email).exists():
            raise Forbidden('User with email \'' + email + '\' already exists', {
                'email': email
            })
        user = User(email = email)
        user.hash_password(password)
        user.save()
        return jsonify(model_to_dict(user))

    def post(self):
        email = request.json.get('email')
        user = User.select().where(User.email == email)
        if not user.exists():
            raise UserNotFound(email)

    def get(self):
        email = request.args.get('email')
        user = User.select().where(User.email == email)
        if not user.exists():
            raise UserNotFound(email)
        return jsonify(model_to_dict(user))

class UserList(Controller):
    def get(self):
        return 'a list of users'
