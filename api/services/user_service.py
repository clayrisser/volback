from api.exceptions.user_exceptions import UserNotFound, UserWithPropExists
from api.exceptions.auth_exceptions import RoleInvalid
from api.models import User
from api.services.peewee_service import query_from_dict
from api.services.auth_service import get_authed_user

def update(id, data):
    authed_user = get_authed_user()
    user = User.select().where(User.id == id).first()
    if not user:
        raise UserNotFound('id', id)
    if 'email' in data:
        user = User.select().where(User.email == data['email']).first()
        if user:
            raise UserWithPropExists('email', data['email'])
    if 'username' in data:
        user = User.select().where(User.username == data['username']).first()
        if user:
            raise UserWithPropExists('username', data['username'])
    if 'role' in data:
        if authed_user.role != 'super_admin':
            raise RoleInvalid('super_admin')
    if 'password' in data:
        user.hash_password(data['password'])
        del data['password']
        user.save()
    user = User.update(**data).where(User.id == id)
    user.execute()
    user = User.select().where(User.id == id).first()
    return user

def find_one(data):
    user = User.select().where(*query_from_dict(User, data)).first()
    if not user:
        raise UserNotFound(data.keys()[0], data[data.keys()[0]])
    return user
