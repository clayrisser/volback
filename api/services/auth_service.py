import jwt
import re
from jwt.exceptions import ExpiredSignatureError, DecodeError
import datetime
from api.models import User
from api.exceptions.user_exceptions import UserNotFound, UserWithPropExists
from api.exceptions.auth_exceptions import (
    TokenInvalid,
    TokenExpired,
    LoggedOut,
    PasswordInvalid,
    RoleInvalid
)
from nails import get_config
from flask import request, make_response
from pydash import _

def renew_access_token():
    user_dict = get_authed_user()
    return get_access_token(user_dict['id']), user_dict

def get_authed_user():
    access_token = request.cookies.get('access_token')
    if not access_token:
        raise LoggedOut()
    payload = get_payload(access_token)
    authed_user = User.select().where(User.id == payload['user_id']).first()
    if not authed_user:
        raise LoggedOut()
    return authed_user

def get_access_token(user_id):
    return jwt.encode({
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=get_config('api', 'jwt.exp')),
        'user_id': user_id
    }, get_config('api', 'jwt.secret'), algorithm='HS256')

def get_payload(access_token):
    try:
        payload = jwt.decode(access_token, get_config('api', 'jwt.secret'), algorithm='HS256')
        if not payload or 'user_id' not in payload:
            raise TokenInvalid()
        return payload
    except ExpiredSignatureError:
        raise TokenExpired()
    except DecodeError:
        raise TokenInvalid()

def resp_with_access_token(data, access_token):
    response = make_response(data)
    domain = get_config('api', 'jwt.domain')
    response.set_cookie(
        key='access_token',
        value=access_token,
        secure=get_config('api', 'jwt.secure'),
        httponly=True,
        expires=datetime.datetime.utcnow() + datetime.timedelta(seconds=get_config('api', 'jwt.exp')),
        domain=(domain if domain else None)
    )
    return response

def update_authed_user(data):
    authed_user = get_authed_user()
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
        authed_user.hash_password(data['password'])
        del data['password']
        authed_user.save()
    if len(data.keys()) > 0:
        User.update(**data).where(User.id == authed_user.id).execute()
    return User.select().where(User.id == authed_user.id).first()

def get_new_username(username, count=None):
    matches = re.findall(r'[^@]+(?=@)', username)
    if len(matches) > 0:
        username = matches[0]
        if User.select().where(User.username == username).exists():
            return get_new_username(username, 1)
        else:
            return username
    else:
        if count == None:
            count = 1
        if User.select().where(User.username == username + str(count)).exists():
            return get_new_username(username, count + 1)
        else:
            return username + str(count)

def guess_user_data(data):
    if 'username' not in data:
        data['username'] = get_new_username(data['email'])
    possible_names = {
        'username': _.snake_case(data['username']).replace('_', ' ').title().split(),
        'display_name': data['display_name'].split() if 'display_name' in data else list()
    }
    if 'first_name' not in data:
        if len(possible_names['display_name']) > 0:
            data['first_name'] = possible_names['display_name'][0]
        else:
            data['first_name'] = possible_names['username'][0]
    if 'last_name' not in data:
        if len(possible_names['display_name']) > 1:
            data['last_name'] = possible_names['display_name'][1]
        elif len(possible_names['username']) > 1:
            data['last_name'] = possible_names['username'][1]
    if 'display_name' not in data:
        data['display_name'] = data['first_name']
        if 'last_name' in data:
            data['display_name'] += ' ' + data['last_name']
    return data

def oauth_register_or_login(data, provider):
    authed_user = User.select().where(User.github == data['github']).first()
    if not authed_user:
        if 'email' in data:
            authed_user = User.select().where(User.email == data['email']).first()
            if authed_user.exists():
                query = {}
                query[provider] = data[provider]
                User.update(**query).where(User.email == data['email']).execute()
                authed_user = User.select().where(User.email == data['email']).first()
                return get_access_token(authed_user.id), authed_user
        data = guess_user_data(data)
        if 'username' in data:
            if User.select().where(User.username == data['username']).exists():
                data['username'] = get_new_username(data['username'])
        if 'password' in data:
            del data['password']
        authed_user = User(**data)
        authed_user.save()
    return get_access_token(authed_user.id), authed_user
